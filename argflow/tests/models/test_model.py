import unittest

from argflow.model import Model


class TestAbstractModel(unittest.TestCase):
    def test_model(self):
        Model.__abstractmethods__ = set()

        class Dummy(Model):
            pass

        d = Dummy('test')
        self.assertIsNone(d.predict('test input'))
        self.assertIsNone(d.save('test path'))
