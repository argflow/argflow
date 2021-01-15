from ..chi import Chi
from ...gaf import Payload, PayloadType

import keras
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from tf_keras_vis.activation_maximization import ActivationMaximization
from tf_keras_vis.utils.callbacks import Print
from tf_keras_vis.utils import find_layer


def generate_model_modifier(layer_name):
    def real_model_modifier(current_model):
        target_layer = current_model.get_layer(name=layer_name)
        new_model = tf.keras.Model(inputs=current_model.inputs, outputs=target_layer.output)
        new_model.layers[-1].activations = tf.keras.activations.linear
        return new_model

    return real_model_modifier


def generate_loss(filter_idx):
    def real_loss(model_output):
        return model_output[..., filter_idx]

    return real_loss


class ActMax(Chi):

    def __init__(self):
        super().__init__()

    def generate(self, x, node, model):
        img_dims = (x.shape[2], x.shape[1])
        if 'layer' in node and 'filter_idx' in node:
            print(node['layer'], node['filter_idx'])
            actmax = self._make_actmax(
                x,
                model,
                node['layer'],
                node['filter_idx']
            )
            return Payload(actmax, PayloadType.IMAGE)
        return Payload(None, None)

    def _make_actmax(self, img_array, model, layer_name, filter_idx, add_text=False):
        layer_idx = model.get_layer(name=layer_name)
        model_modifier = generate_model_modifier(layer_name)
        loss = generate_loss(filter_idx)
        activation_maximization = ActivationMaximization(model, model_modifier, clone=True)

        # Generate max activation
        activation = activation_maximization(loss, callbacks=[Print(interval=50)])
        image = activation[0].astype(np.uint8)
        image = keras.preprocessing.image.array_to_img(image)
        return image
