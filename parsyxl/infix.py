import attr
from parsy import string, regex, generate

from parsyxl import tok
from parsyxl.helpers import generate_with_helper, ResultHelper
from parsyxl.tokens import Token, SurroundedByToken


class InfixOperationToken(Token):
    def __init__(self, name, operation):
        super().__init__(name, operation)

    def find_leftmost_base(self, token=None):
        if token is None:
            token = self.value

        if isinstance(token, Token):
            if isinstance(token, InfixBaseToken):
                return token
            else:
                return self.find_leftmost_base(token.value)
        elif isinstance(token, list):
            if len(token) < 1:
                return False
            return self.find_leftmost_base(token[0])

        return False

    def find_rightmost_base(self, token=None):
        if token is None:
            token = self

        if isinstance(token, Token):
            if isinstance(token, InfixBaseToken):
                return token
            else:
                return self.find_rightmost_base(token.value)
        elif isinstance(token, list):
            if len(token) < 1:
                return False
            return self.find_rightmost_base(token[-1])

        return False


class InfixBaseToken(SurroundedByToken):
    _name = 'BASE'

    def find_leftmost_base(self, *args):
        return self

    def find_rightmost_base(self, *args):
        return self


class InfixWalker():
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def has_tokens(self):
        if len(self.tokens) > (self.position + 1):
            return True
        else:
            return False

    def start(self):
        self.position = 1
        return self.tokens[0]

    def advance(self):
        tokens = self.tokens[self.position:self.position + 2]
        self.position += 2
        return tokens


@attr.s
class InfixConf:
    parser = attr.ib()
    name = attr.ib(default='OP')
    op_type = attr.ib(default='op')

    @op_type.validator
    def check(self, attribute, value):
        if value not in ['op', 'l', 'r']:
            raise ValueError('Operation type must be op, l, or r')

    @property
    def is_r(self):
        return self.op_type == 'r'

    @property
    def is_op(self):
        return self.op_type == 'op'

    @property
    def is_l(self):
        return self.op_type == 'l'


def infix(base, *, e, l_paren=string('('), r_paren=string(')'), eat=regex('[\s]+').optional()):
    """
    Example:
    >>> math = infix((tc.FLOAT | tc.INTEGER).NUMBER.child().flat(), e=[
    >>>    InfixConf(t.ADD | t.SUB, op_type='l'),
    >>>    InfixConf(tc.PIPE, op_type='r'),
    >>>    InfixConf(t.POW | t.MUL | t.DIV, 'MULTIPLICATIVE'),
    >>>    InfixConf(t.ADD | t.SUB, 'ADDITIVE')
    >>> ])
    >>> math.dd('-1+2**(3/5)')
    """
    left_e, op_e, right_e = split_infix(e)

    def make_precedence(upper, myexpr, eat):
        @generate_with_helper
        def precedence(h):
            # Get the base expression. When the infix parser is first called,
            # it will firt try to parse the expression made in top_level_expression().
            yield h(upper << eat)

            while True:
                # Get the operator
                op = yield h.optional(myexpr << eat)
                if not op and h.is_single():
                    # If there is no operator and all we've found so far is one base item,
                    # return that item only. This is so we don't get unnecessary depth in
                    # the tokens. _make_token_mapper() is used to return either the base
                    # object, or an InfixOperationToken.
                    return h.first()
                elif not op:
                    # If we are here, it means the expression cannot be parsed any further
                    # by this precedence.
                    break
                yield h(upper << eat)
            return h.results()

        return precedence

    @generate
    def base_expr():
        left_helper = ResultHelper()
        for left_item in left_e:
            yield left_helper.optional(
                left_item.parser.map(tok(left_item.name))
            )

        base_result = yield base

        right_helper = ResultHelper()
        for right_item in right_e:
            yield right_helper.optional(
                right_item.parser.map(tok(right_item.name))
            )

        return InfixBaseToken(
            base=base_result,
            left=left_helper.results(),
            right=right_helper.results()
        )

    @generate
    def top_level_expr():
        return (yield (l_paren >> bottom_level_precedence << r_paren) | base_expr)

    precedences = [top_level_expr]

    for k, _expr in enumerate(op_e):
        prev = precedences[k]
        next_ = make_precedence(prev, _expr.parser, eat).map(
            _make_token_mapper(_expr.name))
        precedences.append(next_)

    bottom_level_precedence = precedences[-1]
    return bottom_level_precedence


def _make_token_mapper(name):
    def token_mapper(result):
        if isinstance(result, list):
            return InfixOperationToken(name, result)
        else:
            return result

    return token_mapper


def split_infix(data):
    left_e, right_e, op_e = [], [], []
    for expr in data:
        if expr.is_l:
            left_e.append(expr)
        elif expr.is_r:
            right_e.append(expr)
        else:
            op_e.append(expr)
    return left_e, op_e, right_e
