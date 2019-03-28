import unittest
from parsyxl.helpers import ResultsBuilder

class TestParserExtras(unittest.TestCase):
    def test_json(self):
        rb = ResultsBuilder([
            ResultsBuilder(['foo']),
            ResultsBuilder(['bar', 'baz']),
        ])

        print(rb.serializable_with_names())