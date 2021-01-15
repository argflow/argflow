import unittest

from argflow.influence import InfluenceGraph


class TestGraph(unittest.TestCase):

    def test_add_node(self):
        ig = InfluenceGraph()
        ig.add_node(1, activation=12)
        ig.add_node(2, activation=13)
        ig.add_node(3, activation=0)
        self.assertEqual(
            ig.nodes(),
            {
                1: {'activation': 12},
                2: {'activation': 13},
                3: {'activation': 0}
            }
        )

    def test_add_influence(self):
        ig = InfluenceGraph()
        ig.add_node(1, activation=12)
        ig.add_node(2, activation=13)
        ig.add_node(3, activation=0)
        ig.add_influence(1, 2, thing=1)
        ig.add_influence(2, 3, thing=2)
        self.assertEqual(
            ig.influences(),
            [(1, 2, {'thing': 1}), (2, 3, {'thing': 2})]
        )

    def test_remove_node(self):
        ig = InfluenceGraph()
        ig.add_node(1, activation=12)
        ig.add_node(2, activation=13)
        ig.remove_node(2)
        self.assertEqual(
            ig.nodes(),
            {
                1: {'activation': 12}
            }
        )

    def test_remove_influence(self):
        ig = InfluenceGraph()
        ig.add_node(1, activation=12)
        ig.add_node(2, activation=13)
        ig.add_node(3, activation=0)
        ig.add_influence(1, 2, thing=1)
        ig.add_influence(2, 3, thing=2)
        ig.remove_influence(2, 3)
        self.assertEqual(
            ig.influences(),
            [(1, 2, {'thing': 1})]
        )

    def test_influences_from(self):
        ig = InfluenceGraph()
        ig.add_node(1, activation=12)
        ig.add_node(2, activation=13)
        ig.add_node(3, activation=0)
        ig.add_influence(1, 2, thing=1)
        ig.add_influence(2, 3, thing=2)
        self.assertEqual(
            ig.influences_from(1),
            [(1, 2, {'thing': 1})]
        )

    def test_typed_nodes(self):
        ig = InfluenceGraph()
        ig.add_node(1, activation=12)
        ig.add_node(2, activation=13)
        ig.add_node(3, activation=0)
        ig.add_influence(1, 2, thing=1)
        ig.add_influence(2, 3, thing=2)
        start, mid, terminal = ig.get_typed_nodes()
        self.assertEqual(start, [1])
        self.assertEqual(mid, [2])
        self.assertEqual(terminal, [3])