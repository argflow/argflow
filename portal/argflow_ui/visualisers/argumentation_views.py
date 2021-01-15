from argflow_ui.argumentation_graph import ArgumentationGraph, NodeType, Direction, ContributionType


class ArgumentationGraphView:
    """The view of an argumentation graph."""

    def __init__(self, graph: ArgumentationGraph):
        # This should never be modified, make a copy if necessary
        self.graph = graph

    def serialize(self):
        """
        Serializes the argumentation graph view
        """
        return self.graph.serialize()


class GraphArgumentationGraphView(ArgumentationGraphView):
    def __init__(self, graph: ArgumentationGraph):
        super().__init__(graph)
        self.view_nodes = graph.nodes
        self.prune_limit = 20
        self.prune_layer_limit = 5

    def prune_graph(self, limit: int = 20, layer_limit: int = 5):
        """
        Selects a subset of the most important argument nodes based on their
        strength.

        :param limit: The maximum number of nodes in the resulting graph (without inputs and conclusions)
        :param layer_limit: The maximum number of nodes per layer (can encourage deeper graphs if low)
        """
        if self.prune_limit == limit and self.prune_layer_limit == layer_limit:
            # No action required — already pruned
            return

        self.prune_limit = limit
        self.prune_layer_limit = layer_limit

        input_set = set(self.graph.input)
        conclusion_set = set(self.graph.conclusion)
        self.view_nodes = {
            node: self.graph.nodes[node].copy() for node in conclusion_set.union(input_set)
        }
        encountered_nodes = current_layer = conclusion_set

        while limit > 0 and not current_layer.issubset(input_set):
            prev_layer = set()

            for node in current_layer:
                pred = self.graph.predecessors[node]
                prev_layer = prev_layer.union(pred)

            prev_layer = prev_layer.difference(encountered_nodes)
            encountered_nodes = encountered_nodes.union(prev_layer)

            sorted_by_strength = sorted(
                list(prev_layer), key=lambda x: self.graph.nodes[x].get("strength", 0), reverse=True
            )

            selected_nodes = set(sorted_by_strength[: min(limit, layer_limit)])

            # Add up to layer_limit strongest arguments from the current layer
            for selected_node in selected_nodes:
                self.view_nodes[selected_node] = self.graph.nodes[selected_node].copy()

            limit -= len(selected_nodes)
            current_layer = selected_nodes

        self.__compute_useful_nodes_links()

    def __compute_useful_nodes_links(self):
        """
        Computes the links between the useful nodes. Should be called each time these change.

        :param useful_nodes: The selected useful nodes
        """
        # Only link to useful children
        for node, value in self.view_nodes.items():
            children = {
                k: v for k, v in self.graph.nodes[node]["children"].items() if k in self.view_nodes
            }
            self.view_nodes[node]["children"] = children

        # Add indirect links between useful nodes if necessary
        for useful_node_id in self.view_nodes.keys():
            self.__find_indirect_links(useful_node_id)

    def __find_indirect_links(self, node_id):
        """
        Finds useful nodes that should be connected to an input by an indirect link
        and adds such indirect links.

        :param node_id: The ID of the given input
        :param useful_nodes: The useful nodes selected by the pruning algorithm
        """
        useful_node_ids = set(self.view_nodes.keys())
        stack = [node_id]

        while stack:
            current = stack.pop()
            children = self.graph.nodes[current]["children"].keys()
            pruned_children = set(children).difference(useful_node_ids)

            stack.extend(list(pruned_children))

            useful_children = set(children).difference(pruned_children)

            for useful_child in useful_children:
                if useful_child not in self.graph.nodes[node_id]["children"]:
                    # make indirect link
                    self.view_nodes[node_id]["children"][useful_child] = {
                        "contribution_type": ContributionType.INDIRECT
                    }

    def serialize(self):
        """
        Serializes the argumentation graph view
        """
        serialized_gaf = self.graph.serialize()
        serialized_gaf["nodes"] = self.view_nodes
        serialized_gaf["total_nodes"] = (
            len(self.graph.nodes) - len(self.graph.input) - len(self.graph.conclusion)
        )
        return serialized_gaf


class ConversationArgumentationGraphView(ArgumentationGraphView):
    def __init__(self, graph: ArgumentationGraph, primary=None, secondary=[]):
        super().__init__(graph)
        self.__set_primary(primary)
        self.secondary = secondary
        self.interaction_result = None

    def __set_primary(self, primary=None):
        """
        Sets the primary node

        :param primary: The new primary node
        """
        if primary is None:
            # Try to select primary node automatically
            self.primary = self.graph.conclusion[0] if len(self.graph.conclusion) >= 1 else None
            if self.primary is None:
                raise ValueError("Primary node was not provided and could not be derived")
        else:
            self.primary = primary

    def set_state(self, primary=None, secondary=[]):
        """
        Sets the state of the primary and secondary nodes

        :param primary: The new primary node
        :param secondary: The new secondary nodes
        """
        self.__set_primary(primary)
        self.secondary = secondary

    def perform_interaction(self, target, direction, contribution_type, limit):
        """
        Performs the interaction with the given direction on the specified target.

        :param target: The ID of the target node
        :param direction: The direction of the interaction
        """
        if target not in self.graph.nodes:
            raise ValueError("Attempting to interact with non-existent node")
        if direction == Direction.FROM:
            contributions = self.graph.query_targets(
                target, contribution_type=contribution_type, limit=limit
            )
        if direction == Direction.TO:
            contributions = self.graph.query_factors(
                target, contribution_type=contribution_type, limit=limit
            )

        selected_contributions = self.__process_contributions(target, contributions, limit)

        self.interaction_result = selected_contributions

        return selected_contributions

    def possible_interactions(self):
        """
        Returns possible interactions with the graph
        """
        interactions = []
        self.__add_node_interactions(self.primary, interactions)
        for node in self.secondary:
            self.__add_node_interactions(node, interactions)
        return interactions

    def __add_node_interactions(self, node, interactions):
        """
        Adds possible interactions of the given node to the supplied list.

        :param node: Node that is the main target of the interaction
        :param interactions: List of interactions
        """
        if self.graph.nodes[node]["node_type"] != NodeType.CONCLUSION:
            interactions.append({"node": node, "direction": Direction.FROM})
        if self.graph.nodes[node]["node_type"] != NodeType.INPUT:
            interactions.append({"node": node, "direction": Direction.TO})

    def __process_contributions(self, node, contributions, limit, preserve_pointers=False):
        """
        Prunes the returned contributions and updates pointers if necessary.

        :param node: Node for which contributions were queried
        :param contributions: All relevant contributions from/to the given node
        :param limit: The maximum number of contributions to return
        :param preserve_pointers: Specifies whether to preserve the pointers
        """
        if limit is not None:
            sorted_contributions = sorted(
                contributions, key=lambda c: (-self.graph.nodes[c["endpoint"]]["strength"])
            )
            contributions = sorted_contributions[:limit]
        if not preserve_pointers:
            self.primary = node
            self.secondary = [contribution["endpoint"] for contribution in contributions]
        return contributions

    def serialize(self):
        """
        Serializes the argumentation graph view
        """
        return {
            "explanation": self.graph.serialize(),
            "interactions": self.possible_interactions(),
            "interaction_result": self.interaction_result,
        }