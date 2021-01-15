# Mappers

## Abstract Mappers

### InfluenceMapper

Abstract class that transforms a neural network model into an influence graph, based on some input x.

#### Abstract Class

```python
class InfluenceMapper(ExtractorMapper):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def apply(self, model, x):
        pass

```

#### Implementation Example

```python
class DefaultConvolutionalInfluenceMapper(InfluenceMapper):
    def __init__(self, no_filters=10, decoder_function=None):
        super().__init__()
        self.no_filters = no_filters

    def apply(self, model, x):
        influences = InfluenceGraph()

        layers = copy.copy(model.layers)
        layers.reverse()

        classifier_layers = []
        last_conv_layer = None

        for layer in layers:
            if not (isinstance(layer, keras.layers.Conv2D)):
                classifier_layers.append(layer)
            else:
                last_conv_layer = layer
                break
        classifier_layers.reverse()

        if last_conv_layer is None:
            raise Exception('Could not detect any convolutional layers')

        relevant_features = self.get_relevant(
            model, x, last_conv_layer, classifier_layers
        )

        preds = model.predict(x)
        influences.add_node('Prediction')
        predicted_class = model.predict_classes(x)
        confidence = model.predict_proba(x)

        influences.add_node('Input', grad=0)

        for layer, idx, grad in relevant_features:
            influences.add_node(
                f'Filter {idx}', layer=layer, filter_idx=idx, grad=grad)
            influences.add_influence(f'Filter {idx}', 'Prediction')
            influences.add_influence('Input', f'Filter {idx}')

        return influences, predicted_class, confidence

    def get_relevant(self, model, x, last_conv_layer, classifier_layers):
        last_conv_layer_model = keras.Model(
            model.inputs, last_conv_layer.output)

        # Create a model that maps the activations of the last conv
        # layer to the final class predictions
        classifier_input = keras.Input(shape=last_conv_layer.output.shape[1:])
        y = classifier_input
        for layer in classifier_layers:
            y = layer(y)
        classifier_model = keras.Model(classifier_input, y)

        # Compute the gradient of the top predicted class for our input image
        # with respect to the activations of the last conv layer
        with tf.GradientTape() as tape:
            # Compute activations of the last conv layer and make the tape watch it
            last_conv_layer_output = last_conv_layer_model(x)
            tape.watch(last_conv_layer_output)
            # Compute class predictions
            preds = classifier_model(last_conv_layer_output)
            top_pred_index = tf.argmax(preds[0])
            top_class_channel = preds[:, top_pred_index]

        # This is the gradient of the top predicted class with regard to
        # the output feature map of the last conv layer
        grads = tape.gradient(top_class_channel, last_conv_layer_output)

        # This is a vector where each entry is the mean intensity of the gradient
        # over a specific feature map channel
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        last_conv_layer_output = last_conv_layer_output.numpy()[0]
        pooled_grads = pooled_grads.numpy()
        # Sort filters by contribution and return list of (layer, filter index, gradient) tuples
        top_pooled_grads = [(last_conv_layer.name, i, pooled_grads[i])
                            for i in (np.abs(pooled_grads)).argsort()[-self.no_filters:]]

        return top_pooled_grads

```

### CharacterisationMapper

Abstract class that provides a mapping from influence graph nodes to arguments, based on an established
argumentation framework.

#### Abstract Class

```python
class CharacterisationMapper(ExtractorMapper):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def apply(self, node):
        pass

```

#### Implementation Example

```python
from argflow.gaf.frameworks import BipolarFramework

class ConvolutionalCharacterisationMapper(CharacterisationMapper):
    def __init__(self):
        super().__init__()

    def apply(self, node):
        return BipolarFramework.ATTACK if node['grad'] < 0 else BipolarFramework.SUPPORT
```

### StrengthMapper

Abstract class that provides a mapping from an influence graph node to a metric of strength, determining
the magnitude of the influence it has on its children.

#### Abstract Class

```python
class StrengthMapper(ExtractorMapper):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def apply(self, node):
        pass

```

#### Implementation Example
```python
class ConvolutionalStrengthMapper(StrengthMapper):
    def __init__(self):
        super().__init__()
        
    def apply(self, node):
        return np.abs(node['grad']) if 'grad' in node else None
```

## Default Concrete Implementations

```python
from argflow.gaf import default_mappers
```

### DefaultConvolutionalInfluenceMapper
Generates a 3-layer influence graph: the input influences the final convolutional layer which influences the output.

### DefaultConvolutionalCharacterisationMapper
Generates a characterisation from the [`BipolarFramework`](../frameworks): `SUPPORT` if the gradient at the output respect to the feature is positive, `ATTACK` otherwise.

### DefaultConvolutionalStrengthMapper
Assigns a strength equal to the magnitude of the gradient at the output with respect to the feature.

### Example usage
Demo using standard mappers on VGG16.

```python
import numpy as np

from PIL import Image
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions

from argflow.influence import InfluenceGraph
from argflow.gaf import GAFExtractor, PayloadType, Payload
from argflow.gaf.frameworks import BipolarFramework
from argflow.gaf.default_mappers import (DefaultConvolutionalInfluenceMapper,
                                         DefaultConvolutionalStrengthMapper,
                                         DefaultConvolutionalCharacterisationMapper)
from argflow.chi.cnn import GradCAM
from argflow.chi import Chi
from argflow.portal import Writer

if __name__ == '__main__':
    # Init model and writer
    model = VGG16(weights='imagenet')
    summaries = Writer('/path/to/resource/dir', 'CNN Demo')

    # Load input
    img_path = 'image.jpg'
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    # Init mappers
    im = DefaultConvolutionalInfluenceMapper(10, decode_predictions)
    cm = DefaultConvolutionalCharacterisationMapper()
    sm = DefaultConvolutionalStrengthMapper()

    # Extract GAF and send to portal
    extractor = GAFExtractor(
        im, sm, cm, GradCAM())
    gaf = extractor.extract(model, x)
    summaries.write_gaf(gaf)

```