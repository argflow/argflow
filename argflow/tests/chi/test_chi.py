import unittest

from argflow.chi import Chi


class TestAbstractChi(unittest.TestCase):
    def test_chi(self):
        Chi.__abstractmethods__ = set()

        class Dummy(Chi):
            pass

        d = Dummy()
        self.assertIsNone(d.generate('input', 'node', 'model'))
