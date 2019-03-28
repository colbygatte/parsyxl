import unittest
from parsyxl import *

class TestTokenDumper(unittest.TestCase):
    def test_token_shows_strings_in_list(self):
        dumper = TokenDumper()

        parser = seq(string('{"').tok('lbrace'), string('#'))

        token = parser.parse('{"#')

        dump = dumper.dump(token)

        self.assertEqual("""list:2[
|   
|   [0] lbrace: "{""
|   [1] (string): "#"
|   
|   ]%
        """.strip(), dump.strip())
    