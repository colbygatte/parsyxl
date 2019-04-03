from functools import wraps

from parsy import generate

import parsyxl
from parsyxl.tokendumper import *


def generate_tok(thing):
    return wraps(thing)(generate(thing).map(parsyxl.tok(thing.__name__)))


class Token:
    def __init__(self, name=None, value=None, **kwargs):
        self.name = name if name else None
        self.value = value
        self.kwargs = kwargs

    def getkwa(self, name, default=None):
        return self.kwargs.get(name, default)

    def __repr__(self):
        return TokenDumper().dump(self)

    def __str__(self):
        return _to_str(self.value)

    def __add__(self, other):
        return Token(None, [self.value, other])

    def __radd__(self, other):
        return Token(None, [other, self.value])

    def __iadd__(self, other):
        if type(other) is tuple:
            self.extend(other)
        else:
            self.value += other
        return self

    def __getattr__(self, name):
        if name not in self.kwargs:
            raise AttributeError
        else:
            return self.kwargs[name]

    def __eq__(self, other):
        return self.value == other


class CustomToken(Token):
    _name = None
    _args = None

    def __init__(self, *args, tname=None, **kwargs):
        self.__dict__['_frozen'] = False

        parsed_args = []
        if tname is None:
            tname = self._name
        if args is not None:
            parsed_args.extend(args)
        if len(parsed_args) != len(self._args):
            if len(parsed_args) > 0:
                start_index = len(parsed_args) - 1
            else:
                start_index = 0
            for index in range(start_index, len(self._args)):
                named = self._args[index]
                arg = kwargs.get(named)
                parsed_args.append(arg)
        super().__init__(tname, parsed_args)

    def freeze(self):
        self.__dict__['_frozen'] = True

    def set(self, name, value):
        index = self._args.index(name)
        self.value[index] = value

    def __getattr__(self, name):
        if name in self._args:
            return self.value[self._args.index(name)]
        else:
            raise AttributeError('Invalid attribute: %s' % name)


class SurroundedByToken(CustomToken):
    _name = 'SURROUNDED'
    _args = ['left', 'base', 'right']


def _to_str(value, ):
    if type(value) is list:
        return ''.join(_to_str(i) for i in value)
    elif type(value) is Token:
        return _to_str(value.value)
    elif value is None:
        return ''
    else:
        return str(value)
