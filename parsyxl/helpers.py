import json
from parsy import generate, success

from parsyxl.tokens import Token


class BaseEvaluator:
    def __init__(self, token):
        """
        :param token: Highest level token to parse
        """
        self.token = token

    def run(self):
        return self.eval(self.token)

    def eval(self, token):
        rb = ResultsBuilder([])

        if isinstance(token, list):
            rb.extend(self.eval(r) for r in token)
            return rb

        if isinstance(token, Token) and hasattr(self, 'eval_%s' % token.name):
            subrb = ResultsBuilder(token.name)
            rb += subrb
            getattr(self, 'eval_%s' % token.name)(token, subrb)
        else:
            self.eval_default(token, rb)

        return rb

    def eval_default(self, token, rb):
        pass


class ResultsBuilder:
    def __init__(self, *args, **meta):
        self.name = None
        self.items = []
        self._meta = meta
        if len(args) == 1:
            if type(args[0]) is str:
                self.name = args[0]
            else:
                self.items = list(args[0])
        elif len(args) > 1:
            self.name = args[0]
            self.items = list(args[1])
    
    def meta(self, **meta):
        self._meta = meta

    def to_front(self, item):
        if not isinstance(item, list):
            item = list([item])
        self.items = item + self.items
        return self

    def serializable(self):
        data = []

        for i in self.items:
            if isinstance(i, ResultsBuilder):
                data.extend(i.serializable())
            else:
                data.append(i)

        return data

    def serializable_with_names(self):
        data = []

        for i in self.items:
            if isinstance(i, ResultsBuilder):
                data.append(i.serializable_with_names())
            else:
                data.append(str(i))

        return {
            'name': self.name,
            'data': data,
            'meta': self._meta
        }

    def __lshift__(self, other):
        self.items = list(other)
        return self

    def __getattr__(self, name):
        return getattr(self.items, name)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return ''.join(str(i) for i in self.items)

    def __repr__(self):
        return repr(self.items)

    def __iadd__(self, other):
        if type(other) is list:
            self.extend(other)
        else:
            self.append(other)
        return self


class ResultHelper:
    def __init__(self):
        self._results = []

    def results(self, *, single_if_one=False):
        if single_if_one and len(self._results) == 1:
            return self._results[0]
        else:
            return self._results

    def into(self, cls):
        return cls(*self._results)

    def optional(self, parser=None, default_tok=None, default_val=None):
        if parser is None:
            if default_tok:
                return Token(default_tok, default_val)
            else:
                return success('')

        def callback(result):
            if result is not None:
                self._results.append(result)
            elif default_tok:
                self._results.append(Token(default_tok))
            return result
        return parser.optional().map(callback)

    def is_single(self):
        return len(self._results) == 1

    def first(self):
        return self._results[0]

    def __call__(self, parser):
        def callback(result):
            self._results.append(result)
            return result
        return parser.map(callback)

    def __setitem__(self, key, value):
        self._results[key] = value
        return self

    def __getitem__(self, key):
        return self._results[key]

    def __len__(self):
        return len(self._results)


def generate_with_helper(func):
    def callback():
        h = ResultHelper()
        return func(h)
    return generate(callback)
