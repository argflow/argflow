import copy
import keras
import numpy as np
import tensorflow as tf

from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions

from argflow.influence import InfluenceGraph
from argflow.gaf import GAFExtractor, CharacterisationMapper, StrengthMapper, InfluenceMapper
from argflow.gaf.frameworks import BipolarFramework
from argflow.chi.cnn import GradCAM, ActMax
from argflow.portal import Writer


def default_decoder_function(preds, model, input):
    class_pred = model.predict_classes(input)
    certainty = model.predict_proba(input)
    return class_pred, certainty


def default_strength_function(node):
    return np.abs(node['grad']) if 'grad' in node else None


def default_characterisation_function(node):
    return BipolarFramework.ATTACK if node['grad'] < 0 else BipolarFramework.SUPPORT


class DefaultConvolutionalInfluenceMapper(InfluenceMapper):
    def __init__(self, no_filters=10, decoder_function=None):
        super().__init__()
        self.no_filters = no_filters
        if decoder_function is None:
            self.decoder_function = None
        else:
            self.decoder_function = decoder_function

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
        if self.decoder_function is not None:
            _, predicted_class, confidence = decode_predictions(preds, top=1)[0][0]
        else:
            predicted_class, confidence = default_decoder_function(preds, model, x)

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


class DefaultConvolutionalStrengthMapper(StrengthMapper):
    def __init__(self, strength_function=None):
        super().__init__()
        if strength_function is None:
            self.strength_function = default_strength_function
        else:
            self.strength_function = strength_function

    def apply(self, node):
        return self.strength_function(node)


class DefaultConvolutionalCharacterisationMapper(CharacterisationMapper):
    def __init__(self, characterisation_function=None):
        super().__init__()
        if characterisation_function is None:
            self.characterisation_function = default_characterisation_function
        else:
            self.characterisation_function = characterisation_function

    def apply(self, node):
        return self.characterisation_function(node)
