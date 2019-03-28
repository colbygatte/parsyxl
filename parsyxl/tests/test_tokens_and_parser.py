import unittest

from parsyxl import *


class TestTokTest(unittest.TestCase):
    def test_token(self):
        parser = string('{').map(tok('brace'))
        token = parser.parse('{')

        self.assertIsInstance(token, Token)
        self.assertEqual(token.name, 'brace')

    def test_shorthand_token_syntax(self):
        parser = string('{').map(tok('BRACE'))
        token = parser.parse('{')

        self.assertIsInstance(token, Token)
        self.assertEqual(token.name, 'BRACE')

    def test_multi_token(self):
        parser = string('{').map(tok('lbrace')) + string('}').map(tok('rbrace'))
        token = parser.parse('{}')

        self.assertIsInstance(token, Token)

        self.assertIsInstance(token + 'hello', Token)
        self.assertEqual('{}hello', str(token + 'hello'))

        self.assertIsInstance('hello' + token, Token)
        self.assertEqual('hello{}', str('hello' + token))

        self.assertEqual('{}', str(token))
        id1 = id(token)
        token += 'hello'
        id2 = id(token)
        self.assertEqual('{}hello', str(token))
        self.assertTrue(id1 == id2)

    def test_can_concat_tokens(self):
        parser = string('{').map(tok('BRACE')).many().map(joiner).map(tok('BRACES'))
        token = parser.parse('{{{')

        self.assertIsInstance(token, Token)
        self.assertEqual('BRACES', token.name)

    def test_tok_decorator(self):
        @generate_tok
        def parser_one():
            x = yield string('x')
            return x

        one = parser_one.parse('x')
        self.assertEqual('parser_one', one.name)
        self.assertEqual('x', str(one))
