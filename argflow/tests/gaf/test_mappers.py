import unittest

from argflow.gaf.mappers import InfluenceMapper, CharacterisationMapper, StrengthMapper, ExtractorMapper


class TestAbstractMappers(unittest.TestCase):
    def test_influence_mapper(self):
        InfluenceMapper.__abstractmethods__ = set()

        class Dummy(InfluenceMapper):
            pass

        d = Dummy()
        self.assertIsNone(d.apply('model', 'input'))

    def test_strength_mapper(self):
        StrengthMapper.__abstractmethods__ = set()

        class Dummy(StrengthMapper):
            pass

        d = Dummy()
        self.assertIsNone(d.apply('node'))

    def test_characterisation_mapper(self):
        CharacterisationMapper.__abstractmethods__ = set()

        class Dummy(CharacterisationMapper):
            pass

        d = Dummy()
        self.assertIsNone(d.apply('node'))

    def test_base_mapper(self):
        ExtractorMapper.__abstractmethods__ = set()

        class Dummy(ExtractorMapper):
            pass

        d = Dummy()
        self.assertIsNone(d.apply())
