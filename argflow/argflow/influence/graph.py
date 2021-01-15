import networkx as nx


class InfluenceGraph:

    def __init__(self):
        self._G = nx.DiGraph()

    def add_node(self, node, **attributes):
        self._G.add_node(node, **attributes)

    def remove_node(self, node):
        self._G.remove_node(node)

    def add_influence(self, u, v, **attributes):
        self._G.add_edge(u, v, **attributes)

    def remove_influence(self, u, v):
        self._G.remove_edge(u, v)

    def nodes(self):
        """
        Get all nodes in the graph.
        """
        return dict(self._G.nodes(data=True))

    def influences(self):
        """
        Get all influences (edges) in the graph.
        """
        return list(self._G.edges(data=True))

    def influences_from(self, node):
        """
        Get all influences (edges) leaving a node.

        node            - a node.
        """
        return list(self._G.edges(node, data=True))

    def get_typed_nodes(self):
        """
        Infer node types (starting, intermediate, terminal) from
        what's connected to what.

        Starting nodes have no edges going into them.
        Terminal nodes have no edges leaving them.
        Intermediate have nodes entering and leaving them.
        """
        start_nodes = set(self._G.nodes())
        non_start_nodes = set()
        terminal_nodes = set(self._G.nodes())
        for u, v in list(self._G.edges):
            if v in start_nodes:
                start_nodes.remove(v)
                non_start_nodes.add(v)
            if u in terminal_nodes:
                terminal_nodes.remove(u)
        non_start_nodes = non_start_nodes.difference(terminal_nodes)
        return list(start_nodes), list(non_start_nodes), list(terminal_nodes)
