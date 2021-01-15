# Portal

A set of utilities for working with the portal.

## Writer

A utility for sending GAFs to the portal.

### Constructor

#### `Writer(root_dir, model_name)`

- `root_dir` - the directory where all visualisations are saved
- `model_name` - the name of the model (this will be used to create a directory to store explanations)

!!! warning
    Don't forget to set the portal's resources path to the `root_dir` too!

### Methods

#### `write_gaf(gaf, name=None)`

Write a GAF for visualisation in the portal.

- `gaf` - the GAF to be saved
- `name` - the name of the saved GAF (if `None`, will default to a timestamp)

## ExplanationGenerator

An abstract class from which all portal explanation generators derive.

```python
from argflow.portal import ExplanationGenerator
```

### Methods

#### `generate(resource_path, model_name, model_input, explanation_name, chi_value)`

Generates an explanation for a given input. Typically called by the portal.

- `resource_path` - path to the portal resource directory
- `model_name` - name of the model (used for grouping explanations)
- `model_input` - input to the model
- `explanation_name` - a unique name for the generated explanation
- `chi_value` - the chi function used

```python



class SimpleInfluenceMapper(InfluenceMapper):
    def apply(self, model, x):
        influences = InfluenceGraph()
        x_tensor = tf.convert_to_tensor([x], dtype=tf.float32)

        # Calculate d output / d x_tensor
        model_headless = Sequential(model.layers[:-1])
        with tf.GradientTape() as g:
            g.watch(x_tensor)
            output = tf.squeeze(model_headless(x_tensor))
        gradients = tf.squeeze(g.gradient(output, x_tensor))
        pred_label = f"Predicted {tf.math.argmax(output).numpy()}"
        influences.add_node(pred_label)

        for i, feature in enumerate(x):
            influences.add_node(f"Feature {i}", grad=gradients[i].numpy(), value=feature)
            influences.add_influence(f"Feature {i}", pred_label)

        return influences, int(tf.math.argmax(output).numpy()), 0.7


class SimpleStrengthMapper(StrengthMapper):
    def apply(self, node):
        return np.abs(node["grad"]) if "grad" in node else None


class SimpleCharacterisationMapper(CharacterisationMapper):
    def apply(self, node):
        return BipolarFramework.ATTACK if node["grad"] < 0 else BipolarFramework.SUPPORT


class IdentityChi(Chi):
    def generate(self, x, node, model):
        return Payload(node["value"] if "value" in node else "node", PayloadType.STRING)



class DefaultExplanationGenerator(ExplanationGenerator):
    def generate(
        self,
        resource_path: str,
        model_name: str,
        model_input: str,
        explanation_name: str,
        chi_value: str,
    ):
        # Load model (assume a simple feedforward neural network)
        model = keras.models.load_model(os.path.join(resource_path, model_name, "model"))

        # Read input (a Python expression for a vector)
        x = ast.literal_eval(model_input)

        # Set up summary writer
        summaries = Writer(resource_path, model_name)

        # Extract GAF
        extractor = GAFExtractor(SimpleInfluenceMapper(),
                                 SimpleStrengthMapper(),
                                 SimpleCharacterisationMapper(),
                                 IdentityChi())
        gaf = extractor.extract(model, x)

        # Write summaries
        return summaries.write_gaf(gaf, name=explanation_name)

```
