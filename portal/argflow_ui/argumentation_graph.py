from enum import Enum


class ContributionType(str, Enum):
    SUPPORT = "support"
    ATTACK = "attack"
    NEUTRAL = "neutral"
    INDIRECT = "indirect"


class NodeType(str, Enum):
    REGULAR = "regular"
    CONCLUSION = "conclusion"
    INPUT = "input"
    NONE = "none"


class NodeContentType(str, Enum):
    IMAGE = "image"
    STRING = "string"
    WDCLOUD = "wdcloud"


class Direction(str, Enum):
    FROM = "from"
    TO = "to"


class ArgumentationGraph:
    """The full argumentation graph."""

    def __init__(self, explanation, primary=None, secondary=[]):
        self.name = explanation["name"]
        self.input = explanation["input"]
        self.conclusion = explanation["conclusion"]
        self.nodes = explanation["nodes"]

        # Build an auxiliary table of predecessors of each node
        self.predecessors = {node_id: set() for node_id in self.nodes.keys()}
        for node_id, node in self.nodes.items():
            for child_id in node["children"].keys():
                child_id = child_id
                self.predecessors[child_id].add(node_id)

    def query_factors(
        self,
        target,
        contribution_type=None,
        limit=None,
    ):
        """
        Queries for factors that contribute to a target.

        :param target: The ID of the target node
        :param contribution_type: Contribution type (e.g. support, attack)
        :param limit: Limit on the number of returned nodes
        :param preserve_pointers: Specifies whether to keep preserve primary and secondary nodes
        """
        parent_contributions = [
            {"endpoint": node_id, "contribution": self.nodes[node_id]["children"][str(target)]}
            for node_id in self.predecessors[target]
            if contribution_type is None
            or self.nodes[node_id]["children"][target]["contribution_type"] == contribution_type
        ]
        return parent_contributions

    def query_targets(self, source, contribution_type=None, limit=None):
        """
        Queries for nodes the source contributes to.

        :param source: The ID of the source node
        :para contribution_type: Contribution type (e.g. support, attack)
        :param limit: Limit on the number of returned nodes
        :param sort_key_factory: Factory for sort key for determining node priorities
        :param preserve_pointers: Specifies whether to keep preserve primary and secondary nodes
        """
        contributions = [
            {"endpoint": child, "contribution": contribution}
            for child, contribution in self.nodes[source]["children"].items()
            if contribution_type is None or contribution["contribution_type"] == contribution_type
        ]
        return contributions

    def serialize(self):
        """
        Serializes the argumentation graph view
        """
        return {
            "name": self.name,
            "input": self.input,
            "conclusion": self.conclusion,
            "nodes": self.nodes,
        }