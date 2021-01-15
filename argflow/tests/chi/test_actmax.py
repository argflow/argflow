import numpy as np
import tensorflow as tf
import unittest
from PIL import Image

from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten

from argflow.influence import InfluenceGraph
from argflow.gaf import GAFExtractor, PayloadType, Payload
from argflow.gaf.frameworks import BipolarFramework
from argflow.gaf.default_mappers import DefaultConvolutionalInfluenceMapper, DefaultConvolutionalStrengthMapper, \
    DefaultConvolutionalCharacterisationMapper
from argflow.chi.cnn import ActMax
from argflow.chi import Chi


class TestActmax(unittest.TestCase):
    def test_actmax(self):
        # Init model
        model = Sequential()
        model.add(Conv2D(64, kernel_size=3, activation='relu', input_shape=(28, 28, 3), name='conv1'))
        model.add(Conv2D(32, kernel_size=3, activation='relu', name='conv2'))
        model.add(Flatten())
        model.add(Dense(10, activation='softmax'))
        # Prepare input
        x = np.zeros((1, 28, 28, 3))
        node = {'layer': 'conv1', 'filter_idx': 10}
        # Run actmax
        am = ActMax()
        img = am.generate(x, node, model).content

        self.assertEqual(img.size, (28, 28))
