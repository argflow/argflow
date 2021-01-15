import unittest

import numpy as np

from sklearn.naive_bayes import CategoricalNB

from argflow.models import BayesianClassifierModel


class TestBayesPredict(unittest.TestCase):

    def setUp(self):
        rng = np.random.RandomState(1)

        self.X = rng.randint(5, size=(6, 100))
        y = np.array([1, 2, 3, 4, 5, 6])

        model = CategoricalNB()
        model.fit(self.X, y)
        self.model = model

    def test_predict(self):
        """
         Checks that the prediction from the wrapped model is the same as without the wrapper
        """
        bayes_model = BayesianClassifierModel(self.model)
        self.assertAlmostEqual(self.model.predict(
            self.X[2:3]), bayes_model.predict(self.X[2:3]))


if __name__ == '__main__':
    unittest.main()
