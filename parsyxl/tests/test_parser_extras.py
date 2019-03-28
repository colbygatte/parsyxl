import unittest
from parsyxl import regex, string

class TestParserExtras(unittest.TestCase):
    def test_child(self):
        """
        Tests that the parser returns the first child token.
        """
        WORD = regex('[a-zA-Z]+').WORD
        NUM = regex('[0-9]+').NUM

        wordnum = (WORD | NUM).WORDNUM.child()

        self.assertEqual(
            wordnum.parse('foo').name,
            'WORD'
        )
    
    def test_child_with_many(self):
        """
        Tests that the parser returns the first child token.
        """
        WORD = regex('[a-zA-Z]+').WORD
        NUM = regex('[0-9]+').NUM

        wordnum = (WORD | NUM).WORDNUM.child().many().tok() # Note: many() returns a list, calling tok() wraps it in a Token.

        result = wordnum.parse('123abc456')

        names = list(map(lambda i: i.name, result.value))

        self.assertEqual(
            names,
            ['NUM', 'WORD', 'NUM']
        )

    def test_flat(self):
        """
        Tests that the parser flattens the result down to a single token.
        """
        CHAR_A = string('A').CHAR_A
        CHAR_B = string('B').CHAR_B
        CHAR_C = string('C').CHAR_C

        parser = (CHAR_A + CHAR_B + CHAR_C).ABC.flat()

        self.assertEqual(
            parser.parse('ABC').value,
            'ABC'
        )