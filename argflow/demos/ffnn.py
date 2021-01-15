import numpy as np

import keras
from keras import Sequential
from keras.layers import Dense, Softmax, ReLU

import tensorflow as tf

from argflow.influence import InfluenceGraph
from argflow.gaf import GAFExtractor, CharacterisationMapper, StrengthMapper, InfluenceMapper, Payload, PayloadType
from argflow.gaf.frameworks import BipolarFramework
from argflow.chi import Chi
from argflow.portal import Writer


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

        pred_label = tf.math.argmax(output).numpy()
        confidence = max(keras.backend.softmax(output.numpy()))
        influences.add_node('Prediction')

        influences.add_node('Input', grad=0)

        for i, feature in enumerate(x):
            influences.add_node(
                f'Feature {i}', grad=gradients[i].numpy(), value=feature, idx=i)
            influences.add_influence(f'Feature {i}', 'Prediction')
            influences.add_influence('Input', f'Feature {i}')

        return influences, str(pred_label), confidence


class SM(StrengthMapper):
    def apply(self, node):
        return np.abs(node['grad']) if 'grad' in node else None


class CM(CharacterisationMapper):
    def apply(self, node):
        return BipolarFramework.ATTACK if node['grad'] < 0 else BipolarFramework.SUPPORT


class Id(Chi):
    def generate(self, x, node, model):
        return Payload(f'Feature {node["idx"]}', PayloadType.STRING)


if __name__ == '__main__':
    # Init some simple data (y = 1 iff x[0] > 3)
    X = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0],
         [-12, 101], [-15, -51], [2, -121], [3, 11], [44, 541], [5, -591], [16, 1],
         [0, 5], [1, -12], [2, 123], [3, 17], [4, -55], [5, -2], [6, 12]]
    y = [0, 0, 0, 0, 1, 1, 1,
         0, 0, 0, 0, 1, 1, 1,
         0, 0, 0, 0, 1, 1, 1]

    # Init simple binary classifier
    model = Sequential([
        Dense(32, activation='relu',
              kernel_initializer='random_normal', input_dim=2),
        Dense(2, activation='relu', kernel_initializer='random_normal'),
        Softmax()
    ])

    # Train model
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.01),
                  loss=keras.losses.SparseCategoricalCrossentropy(),
                  metrics=['accuracy'])

    model.fit(X, y, epochs=200, verbose=0)
    model.summary()

    extractor = GAFExtractor(
        IM(), SM(), CM(), Id())
    gaf = extractor.extract(model, [0, 0])

    summaries = Writer('../portal/examples/', 'FFNN')
    summaries.write_gaf(gaf)
