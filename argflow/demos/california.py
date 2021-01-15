import copy
import keras
import numpy as np
import pandas as pd
import tensorflow as tf

from keras import Sequential
from keras.layers import Dense, Softmax
from keras.optimizers import RMSprop

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

        feature_names = {0: 'Longitude', 1: 'Latitude', 2: 'Housing Median Age', 3: 'Total Rooms',
                         4: 'Total Bedrooms', 5: 'Population', 6: 'Households', 7: 'Median Income',
                         8: '<1H OCEAN', 9: 'NEAR BAY', 10: 'INLAND', 11: 'NEAR OCEAN', 12: 'ISLAND'}
        influences.add_node('Input', grad=0)
        for i, feature in enumerate(x[0]):
            influences.add_node(
                f'Feature {i}', grad=gradients[i].numpy(), value=feature, fname=feature_names[i], idx=i)
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
        return Payload(f'{node["fname"]} : {round(node["value"], 4)}', PayloadType.STRING)


def load_data():
    output_label = "median_house_value"

    # Use pandas to read CSV data as it contains various object types
    # Feel free to use another CSV reader tool
    # But remember that LabTS tests take Pandas Dataframe as inputs
    data = pd.read_csv("demos/housing_cat.csv")

    # Shuffle data
    data = data.sample(frac=1)

    # Spliting input and output
    x = data.loc[:, data.columns != output_label]
    y = data.loc[:, [output_label]]
    return x, y


def calculate_normalisation_params(x, ocean_proximity_labels):
    input_norm_params = {}
    median_bedrooms = {}
    median_bedrooms = {
        label: float(x[x['ocean_proximity'] == label]
                     ['total_bedrooms'].median())
        for label in ocean_proximity_labels
    }

    for col_name in x:
        if not col_name == 'ocean_proximity':
            input_norm_params[col_name] = (
                float(x[col_name].mean()),
                float(x[col_name].std())
            )
    return input_norm_params, median_bedrooms


def preprocess(x, input_norm_params, median_bedrooms, ocean_proximity_labels, output_category_count=5, y=None):
    # Fill missing values
    for label in ocean_proximity_labels:
        x.loc[x['ocean_proximity'] == label, 'total_bedrooms'] \
            = x[x['ocean_proximity'] == label]['total_bedrooms'].fillna(median_bedrooms[label])

    # One-hot encode ocean proximity
    for label in ocean_proximity_labels:
        label_column = [1 if op ==
                        label else 0 for op in x['ocean_proximity']]
        x.loc[:, label] = label_column
        input_norm_params[label] = (0, 1)
    x = x.drop('ocean_proximity', axis=1)

    # One-hot encode outputs, if present
    for label in range(output_category_count):
        label_column = [1 if cat ==
                        label else 0 for cat in y['median_house_value']]
        y.loc[:, str(label)] = label_column
    y = y.drop('median_house_value', axis=1)

    # Normalise inputs
    for col_name in x:
        mu, sigma = input_norm_params[col_name]
        x.loc[:, col_name] -= mu
        x.loc[:, col_name] /= sigma

    return x, y


def train(x_train, y_train, epochs=20):
    # Init simple binary classifier
    model = Sequential([
        Dense(32, activation='relu',
              kernel_initializer='random_normal',
              input_dim=13, 
              kernel_regularizer=keras.regularizers.l1_l2(l1=1e-3, l2=0),
              bias_regularizer=keras.regularizers.l1_l2(l1=1e-5, l2=0)),
        Dense(5, activation='relu', kernel_initializer='random_normal'),
        Softmax()
    ])
    # Training loop
    model.compile(optimizer=RMSprop(),
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
                  metrics=['accuracy'])
    x, y = x_train.to_numpy(), y_train.to_numpy()
    model.fit(x, y, epochs=epochs)
    return model


if __name__ == '__main__':
    # Load the data
    x, y = load_data()
    no_examples = len(y)

    # Split into train/test sets
    train_cutoff = int(np.floor(no_examples * 0.9))

    x_train = x.iloc[:train_cutoff, :]
    y_train = y.iloc[:train_cutoff, :]

    x_test = x.iloc[train_cutoff:, :]
    y_test = y.iloc[train_cutoff:, :]

    # Calculate params for normalisation
    ocean_proximity_labels = [
        '<1H OCEAN', 'NEAR BAY', 'INLAND', 'NEAR OCEAN', 'ISLAND'
    ]
    input_norm_params, median_bedrooms = calculate_normalisation_params(
        x_train, ocean_proximity_labels
    )

    # Preprocess data
    x_train, y_train = preprocess(
        x_train, input_norm_params, median_bedrooms, ocean_proximity_labels, y=y_train)
    x_test, y_test = preprocess(
        x_test, input_norm_params, median_bedrooms, ocean_proximity_labels, y=y_test)

    # Train model
    model = train(x_train, y_train, epochs=10)

    for i in range(0, 5):
        # Feed model an input
        x_test_ex = x_test.iloc[i:i+1, :].to_numpy()
        y_test_ex = y_test.iloc[i:i+1, :]

        # Extract explanation
        extractor = GAFExtractor(IM(), SM(), CM(), Id())
        gaf = extractor.extract(model, x_test_ex)

        # Write explanation
        summaries = Writer('../portal/examples', 'Cali')
        summaries.write_gaf(gaf, f'Prediction {i}')

        # Show the correct answer
        print('The correct answer was...')
        print(y_test_ex)