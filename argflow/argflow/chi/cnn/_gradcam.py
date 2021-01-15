from ..chi import Chi
from ...gaf import Payload, PayloadType

import keras
import numpy as np
import tensorflow as tf

from matplotlib import cm


class GradCAM(Chi):

    def __init__(self):
        super().__init__()

    def generate(self, x, node, model):
        img_dims = (x.shape[2], x.shape[1])
        if 'layer' in node and 'filter_idx' in node:
            print(node['layer'], node['filter_idx'])
            heatmap = self._make_gradcam_heatmap(
                x,
                model,
                node['layer'],
                node['filter_idx']
            )
            return Payload(self._render_heatmap(x, heatmap, img_dims), PayloadType.IMAGE)
        return Payload(None, None)

    def _render_heatmap(self, img_array, heatmap, size):
        # Rescale heatmap to a range 0-255
        heatmap = np.uint8(255 * heatmap)

        # Use jet colormap to colorize heatmap
        jet = cm.get_cmap("jet")

        # Use RGB values of the colormap
        jet_colors = jet(np.arange(256))[:, :3]
        jet_heatmap = jet_colors[heatmap]

        # Create an image with RGB colorized heatmap
        jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)
        jet_heatmap = jet_heatmap.resize(size)

        jet_heatmap = keras.preprocessing.image.img_to_array(jet_heatmap)
        jet_heatmap = img_array.squeeze() + jet_heatmap * 0.6
        jet_heatmap = keras.preprocessing.image.array_to_img(jet_heatmap)

        return jet_heatmap

    def _make_gradcam_heatmap(self, img_array, model, layer_name, filter_idx):
        # Based on https://github.com/keras-team/keras-io/blob/master/examples/vision/grad_cam.py

        # Create a model that maps the input image to the activations
        # of the conv layer of interest
        intermediate_layer = model.get_layer(layer_name)
        model_till_intermediate_layer = keras.Model(
            model.inputs, intermediate_layer.output)

        intermediate_layer_output = model_till_intermediate_layer(img_array)
        intermediate_layer_output = intermediate_layer_output.numpy()[0]
        intermediate_layer_output = intermediate_layer_output[:, :, filter_idx]

        # Normalise between 0-1
        heatmap = np.maximum(intermediate_layer_output, 0) / \
            np.max(intermediate_layer_output)
        return heatmap
