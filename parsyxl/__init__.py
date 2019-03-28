from parsy import *

import parsyxl.helpers
from parsyxl.infix import *
from parsyxl.tokens import *


class ParserExtras:
    def tok(self, name=None):
        @Parser
        def tok_parser(stream, index, **kwargs):
            result = self(stream, index)
            if result.status:
                return Result.success(result.index, Token(name, result.value, **kwargs))
            else:
                return result

        return tok_parser

    def __getattr__(self, name):
        if name == name.upper():
            return self.tok(name)
        raise AttributeError

    def concat(self):
        def joiner(items):
            return ''.join(str(i) for i in items)

        return self.map(joiner)

    def flat(self):
        @Parser
        def flat_parser(stream, index, **kwargs):
            result = self(stream, index)
            if result.status:
                result.value.value = str(result.value)
                return result
            else:
                return result

        return flat_parser

    def child(self):
        @Parser
        def flat_parser(stream, index, **kwargs):
            result = self(stream, index)
            if result.status:
                return Result.success(result.index, result.value.value)
            else:
                return result

        return flat_parser

    def dd(self, string, d=None):
        if not d:
            d = TokenDumper()
        dump = d.dump(self.parse(string))
        print(dump)
        exit()


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


Parser.tok = ParserExtras.tok
Parser.child = ParserExtras.child
Parser.concat = ParserExtras.concat
Parser.flat = ParserExtras.flat
Parser.dd = ParserExtras.dd
Parser.__getattr__ = ParserExtras.__getattr__


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
