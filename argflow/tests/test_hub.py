import appdirs
import math
import os
import unittest
import tempfile

import argflow.hub as hub

from argflow.models import KerasModel
from argflow.hub._api import _endpoint
from keras.losses import MeanSquaredError
from keras.models import Sequential
from keras.layers import Dense

_resource_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'resources')
_cache_dir = appdirs.user_cache_dir('argflow', 'argflow')


def mock_api_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code=200, json_data=None, content=None):
            self.json_data = json_data
            self.content = content
            self.status_code = status_code

        def json(self):
            return self.json_data

    responses = {
        f'{_endpoint}/api/dataset/university':
            MockResponse(json_data=['some info']),
        f'{_endpoint}/api/dataset/university/download':
            MockResponse(content=open(os.path.join(
                _resource_dir, 'university'), 'rb').read()),
        f'{_endpoint}/api/dataset/bs-dataset':
            MockResponse(json_data=[]),
        f'{_endpoint}/api/model/nn':
            MockResponse(json_data=['some info']),
        f'{_endpoint}/api/model/broken-nn':
            MockResponse(json_data=['some other info']),
        f'{_endpoint}/api/model/nn/download':
            MockResponse(content=open(os.path.join(
                _resource_dir, 'nn'), 'rb').read()),
        f'{_endpoint}/api/model/broken-nn/download':
            MockResponse(content=open(os.path.join(
                _resource_dir, 'university'), 'rb').read()),
        f'{_endpoint}/api/model/bs-model':
            MockResponse(json_data=[]),
    }

    return responses[args[0]]


class TestEmtpyCache(unittest.TestCase):

    def test_empty_cache(self):
        hub.empty_cache()
        self.assertFalse(os.path.exists(_cache_dir))

    def test_double_empty_cache(self):
        hub.empty_cache()
        hub.empty_cache()
        self.assertFalse(os.path.exists(_cache_dir))


class TestRequests(unittest.TestCase):

    @unittest.mock.patch('requests.get', side_effect=mock_api_get)
    def test_load_nonexistent_dataset(self, mock):
        with self.assertRaises(hub.NonExistentHubItemError):
            hub.load_dataset('bs-dataset')

    @unittest.mock.patch('requests.get', side_effect=mock_api_get)
    def test_load_nonexistent_model(self, mock):
        with self.assertRaises(hub.NonExistentHubItemError):
            hub.load_model('bs-model')


class TestLoadModels(unittest.TestCase):

    @unittest.mock.patch('requests.get', side_effect=mock_api_get)
    def test_load_model(self, mock):
        model = hub.load_model('nn')
        self.assertEqual(math.ceil(model.predict([[1, 3]])), 1)

    @unittest.mock.patch('requests.get', side_effect=mock_api_get)
    def test_load_invalid_model(self, mock):
        # This downloads the university dataset instead of a model
        with self.assertRaises(hub.InvalidMetadataError):
            model = hub.load_model('broken-nn')


class TestLoadDatasets(unittest.TestCase):

    @unittest.mock.patch('requests.get', side_effect=mock_api_get)
    def test_load_dataset(self, mock):
        data, data_dir = hub.load_dataset('university')
        self.assertEqual(data_dir, os.path.join(
            _cache_dir, 'dataset', 'university'))
        self.assertTrue((data.iloc[3] == [0, 0, 1, 1, 0]).all())

    @unittest.mock.patch('requests.get', side_effect=mock_api_get)
    def test_train_val_test_split(self, mock):
        train, val, test, _ = hub.load_dataset(
            'university', train_val_test_split=(5, 1, 2))
        self.assertEqual(len(train), 10)
        self.assertEqual(len(val), 2)
        self.assertEqual(len(test), 4)


class TestPackageModels(unittest.TestCase):

    def setUp(self):
        # Init simple binary classifier
        model = Sequential()
        model.add(Dense(32, activation='relu', input_dim=2))
        model.add(Dense(1, activation='sigmoid'))

        self.model = model

    def test_package(self):
        """
        Test if packaging causes a package to be created
        """
        temp = tempfile.TemporaryDirectory()
        keras_model = KerasModel(self.model)
        hub.package_model(keras_model, temp.name, 'model1')
        self.assertTrue(os.path.exists(os.path.join(temp.name, 'model1.zip')))
        temp.cleanup()

    def test_invalid_package(self):
        """
        Test type checks when packaging
        """
        temp = tempfile.TemporaryDirectory()
        with self.assertRaises(TypeError):
            hub.package_model('nonsense', temp.name, 'model1')
        temp.cleanup()


if __name__ == '__main__':
    unittest.main()
