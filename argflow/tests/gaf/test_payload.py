import unittest

from argflow.gaf import Payload, PayloadType


class TestGraph(unittest.TestCase):
    def test_invalid_types(self):
        with self.assertRaises(AssertionError):
            p = Payload('hello', PayloadType.IMAGE)
        with self.assertRaises(AssertionError):
            p = Payload('hello', PayloadType.IMAGE_PAIR)
        with self.assertRaises(AssertionError):
            p = Payload(123, PayloadType.STRING)

    def test_equal(self):
        self.assertEqual(Payload('hello world', PayloadType.STRING),
                         Payload('hello world', PayloadType.STRING))

    def test_not_equal(self):
        self.assertNotEqual(Payload('oioi everyone', PayloadType.STRING),
                            Payload('hello world', PayloadType.STRING))

    def test_different_class(self):
        self.assertNotEqual(Payload('oioi everyone', PayloadType.STRING),
                            'asdf')
