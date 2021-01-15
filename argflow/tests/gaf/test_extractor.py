import os
import json
import unittest

from argflow.influence import InfluenceGraph
from argflow.gaf.mappers import InfluenceMapper, CharacterisationMapper, StrengthMapper
from argflow.chi import Chi
from argflow.gaf import GAF, Payload, PayloadType, NodeType, GAFExtractor
from argflow.gaf.frameworks import BipolarFramework, SupportFramework, TripolarFramework


class DemoIM(InfluenceMapper):
    def apply(self, model, x):
        influences = InfluenceGraph()
        influences.add_node('has leaves', value=1)
        influences.add_node('orange plant', value=2)
        influences.add_node('carrot')
        influences.add_influence('has leaves', 'orange plant')
        influences.add_influence('orange plant', 'carrot')
        return influences, 'carrot', 0.9


class DemoSM(StrengthMapper):
    def apply(self, node):
        return node['value'] if 'value' in node else None


class DemoCM(CharacterisationMapper):
    def apply(self, node):
        return BipolarFramework.SUPPORT


class DemoChi(Chi):
    def generate(self, x, node, model):
        return Payload('Feature', PayloadType.STRING)


class TestGAF(unittest.TestCase):

    def test_simple(self):
        extractor = GAFExtractor(DemoIM(), DemoSM(), DemoCM(), DemoChi())
        extractor.extract('some model', 'some input')
