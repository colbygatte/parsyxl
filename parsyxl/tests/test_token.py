import unittest
import parsyxl.tokens
import functools


class TestNameToken(parsyxl.tokens.CustomToken):
    _name = 'NAME'
    _args = ['first', 'last']


class TestToken(unittest.TestCase):
    def test_name(self):
        t = TestNameToken('J', 'D')

        self.assertEqual('NAME', t.name)

    def test_kwargs(self):
        t = TestNameToken(first='J', last='D')

        self.assertEqual('J', t.first)
        self.assertEqual('D', t.last)

    def test_args(self):
        t = TestNameToken('J', 'D')

        self.assertEqual('J', t.first)
        self.assertEqual('D', t.last)
    
    def test_renaming(self):
        t = TestNameToken(first='J', last='D', tname='FOO')

        self.assertEqual(t.name, 'FOO')
        
    