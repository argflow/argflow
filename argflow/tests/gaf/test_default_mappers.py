import unittest

import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten

from argflow.gaf.frameworks import BipolarFramework
from argflow.gaf.default_mappers import (DefaultConvolutionalCharacterisationMapper,
                                         DefaultConvolutionalInfluenceMapper,
                                         DefaultConvolutionalStrengthMapper)


class TestDefaultConvolutionalMappers(unittest.TestCase):
    def test_default_strength(self):
        sm = DefaultConvolutionalStrengthMapper()
        strength = sm.apply({
            'grad': -30
        })
        self.assertEqual(strength, 30)

    def test_custom_strength(self):
        def custom_mapper(x):
            return 420
        sm = DefaultConvolutionalStrengthMapper(custom_mapper)
        strength = sm.apply({
            'grad': -30
        })
        self.assertEqual(strength, 420)

    def test_default_characterisation(self):
        cm = DefaultConvolutionalCharacterisationMapper()
        c = cm.apply({
            'grad': -30
        })
        self.assertEqual(c, BipolarFramework.ATTACK)

    def test_custom_characterisation(self):
        def custom_mapper(self):
            return BipolarFramework.SUPPORT
        cm = DefaultConvolutionalCharacterisationMapper(custom_mapper)
        c = cm.apply({
            'grad': -30
        })
        self.assertEqual(c, BipolarFramework.SUPPORT)

    def test_default_influence(self):
        # Create basic model
        model = Sequential()
        model.add(Conv2D(64, kernel_size=3, activation='relu',
                         input_shape=(28, 28, 3), name='conv1'))
        model.add(Conv2D(32, kernel_size=3, activation='relu', name='conv2'))
        model.add(Flatten())
        model.add(Dense(10, activation='softmax'))
        # Prepare input
        x = np.zeros((1, 28, 28, 3))
        node = {'layer': 'conv1', 'filter_idx': 10}
        # Init mapper
        im = DefaultConvolutionalInfluenceMapper()
        influences, predicted_class, confidence = im.apply(model, x)
        self.assertEqual(len(predicted_class), 1)
        self.assertEqual(len(confidence), 1)
        self.assertEqual(len(influences.nodes()), 12)
        self.assertEqual(len(influences.influences()), 20)
