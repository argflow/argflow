import unittest

import keras
from keras.losses import MeanSquaredError
from keras.models import Sequential
from keras.layers import Dense

from argflow.models import KerasModel

class TestPredict(unittest.TestCase):

    def setUp(self):
        # Init some simple data (y = 1 iff x[0] = 1)
        X = [[0, 10], [0, 0], [0, 1], [1, 0], [1, 2], [1, -1], [1, 3]]
        y = [0, 0, 0, 1, 1, 1, 1]

        # Init simple binary classifier
        model = Sequential()
        model.add(Dense(32, activation='relu', input_dim=2))
        model.add(Dense(1, activation='sigmoid'))

        # Train model
        model.compile(optimizer='adam', 
                      loss=MeanSquaredError(),
                      metrics=['accuracy'])

        model.fit(X, y, epochs=10, verbose=0)
        self.model = model
        

    def test_predict(self):
        """
        Checks that the prediction from the wrapped model is the same as without the wrapper
        """
        keras_model = KerasModel(self.model)
        self.assertAlmostEqual(self.model.predict([[0,0]]), keras_model.predict([[0,0]]))


if __name__ == '__main__':
    unittest.main()
