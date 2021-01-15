# Influences

Class that abstracts the process of constructing a graph using networkx and the notion of influences, used in conjunction
with influence, characterisation and strength mappers to produce a GAF.

## Required Librearies

```python
import networkx as nx
```

## Methods

### `add_node(self, node, **attributes)`

Class method for adding a node with the specified attributes to the underlying graph.

### `remove_node(self, node)`

Class method to remove a node from the influence graph.

### `add_influence(self, u, v, **attributes)`

Class method to add an influence from argument `u` to argument `v` in the influence graph.
This is accomplished by adding an edge to the underlying `networkx` graph.

### `remove_influence(self, u, v)`

Class method to remove an influence from argument `u` to argument `v`.


### `nodes(self)`

Class method to retrieve all nodes in the graph.

### `influences(self)`

Class method to retrieve all influences (edges) in the graph.

### `influences_from(self, node)`

Class method to retrieve all influences (edges) leaving a node (all nodes an argument is influencing).

### `get_typed_nodes(self)`

Class method to retrieve nodes and infer their types (starting, intermediate, terminal) from the existing
connections.
