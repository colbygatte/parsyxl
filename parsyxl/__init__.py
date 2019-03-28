from parsy import *

import parsyxl.helpers
from parsyxl.infix import *
from parsyxl.tokens import *

"""
Mappers
"""

class Mapper:



def tok(name=None):
    def tok_map(result):
        return Token(name, result)

    return tok_map


def child(result):
    return result.value


def flatten(result):
    result.value = str(result.value)
    return result


def joiner(items):
    return ''.join(str(i) for i in items)


"""
Other
"""


def dd(parser, string, d=None):
    if not d:
        d = TokenDumper()
    dump = d.dump(parser.parse(string))
    print(dump)
    exit()


"""
Parsers
"""


def quoted(l='"', r='"', escape='\\'):
    """
    Parse quoted strings.

    >>> quoted('<<', '>>').parse('<<Hi \>> there>>')
    Hi >> there
    """
    escape_parser = string(escape) >> string(r)

    @generate
    def quoted_fn():
        yield string(l)

        found = ''
        while True:
            found_escape_char = yield until_string([r, escape]).optional()

            if found_escape_char:
                found += found_escape_char
                found_escape_sequence = yield escape_parser.many().concat().optional()
                if found_escape_sequence:
                    found += found_escape_sequence
                continue
            else:
                break

        found += yield until_string(r)
        yield string(r)
        return found

    return quoted_fn


def delimited(expression, l='(', r=')', sep=','):
    """
    Parse a deliminited list.
    """
    white = regex('[\s]+').optional()
    if type(sep) is str:
        sep = white >> string(sep) << white

    @generate
    def csv_fn():
        yield string(l) << white

        found = []
        while True:
            test = yield expression.optional()
            if test:
                found.append(test)
                test_comma = yield sep.optional()
                if not test_comma:
                    break
            else:
                break

        yield white >> string(r)
        return found

    return csv_fn


def not_char(char):
    char = list(char)

    @Parser
    def not_char_parser(stream, index):
        if stream[index] in char:
            return Result.failure(index, 'Found %s while looking for char other than %s.' % (
                stream[index],
                ', '.join(char)
            ))
        else:
            return Result.success(index + 1, stream[index])

    return not_char_parser


def not_string(test):
    @Parser
    def not_str_parser(stream, index):
        if len(test) >= len(stream) - index:
            from_stream = stream[index:index + len(test)]
            if from_stream != test:
                return Result.success(index + len(test), from_stream)
            else:
                return Result.failure(index, 'not %s' % test)

    return not_str_parser


def until_string(test, *, consume=False):
    """
    Match up to a string.
    """

    if type(test) is not list:
        test = list([test])

    @Parser
    def until_string_parser(stream, index):
        found = ''

        for char in stream[index:]:
            for t in test:
                if stream[index + len(found):index + len(found) + len(t)] == t:
                    if consume:
                        return Result.success(index + len(found) + len(t), found)
                    else:
                        return Result.success(index + len(found), found)
            found += char

        return Result.failure(index, 'never found %s' % ','.join(test))

    return until_string_parser
