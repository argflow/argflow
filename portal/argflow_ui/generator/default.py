import ast
import os

import keras
import numpy as np
import tensorflow as tf

from keras import Sequential
from argflow.chi import Chi
from argflow.gaf.frameworks import BipolarFramework
from argflow.influence import InfluenceGraph
from argflow.portal import Writer
from argflow.gaf import (
    GAFExtractor,
    InfluenceMapper,
    CharacterisationMapper,
    StrengthMapper,
    Payload,
    PayloadType,
)

from argflow.portal import ExplanationGenerator


class IM(InfluenceMapper):
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


class SM(StrengthMapper):
    def apply(self, node):
        return np.abs(node["grad"]) if "grad" in node else None


class CM(CharacterisationMapper):
    def apply(self, node):
        return BipolarFramework.ATTACK if node["grad"] < 0 else BipolarFramework.SUPPORT


class Ident(Chi):
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
        # Load model
        model = keras.models.load_model(os.path.join(resource_path, model_name, "model"))

        # Load input (TODO: make this sane)
        x = ast.literal_eval(model_input)

        # Set up summary writer
        summaries = Writer(resource_path, model_name)

        # Extract GAF
        extractor = GAFExtractor(IM(), SM(), CM(), Ident())
        gaf = extractor.extract(model, x)

        # Write summaries
        return summaries.write_gaf(gaf, name=explanation_name)
