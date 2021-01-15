# Generalised Argumentation Framework

The GAF class is the abstract representation of the structure of the most relevant arguments and the relations between them for the model to be explained.

### Constructor

#### `GAF(confidence, predicted_class)`

Create a GAF to be shaped by the GAFExtractor.

- `confidence` - confidence of the prediction

- `predicted_class` - class predicted by the model

### Methods

#### `add_argument(node, strength, payload)`

Class method to add an argument to the graph.

#### `add_input(node, payload)`

Class method to add the input node to the graph.

#### `add_conclusion(node, confidence, predicted_class, payload)`

Class method to add the conclusion node to the graph.

#### `remove_node(node)`

Class method to remove a node from the graph.

#### `add_relation(u, v, relation)`

Class method to add a relation between two nodes (u, v).

#### `remove_relation(u, v)`

Class method to remove a relation between two nodes (u, v).

#### `arguments()`

Class method to get all arguments in the GAF.

#### `inputs()`

Class method to get all inputs in the GAF.

#### `conclusions()`

Class method to get all conclusions in the GAF.

#### `relations_from(node)`

Class method to get all relations (edges) leaving a node.

#### `serialise(name, root_dir, payloads_dir)`

Method used to serialise GAFs. This is very important for the communication between the library and the portal, as it transforms the GAFs to a JSON format and places the result in a common directory for it to be able to be processed by the portal API.

- `name` - name of the GAF

- `root_dir` - path to the directory where all visualisations are saved. Portal points to this directory as well

- `payloads_dir` - path to save the payloads relative to the root.
