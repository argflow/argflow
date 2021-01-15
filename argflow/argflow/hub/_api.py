import appdirs
import json
import math
import os
import shutil
import requests
import pandas as pd

from ._keras import load_keras as _load_keras

from configparser import ConfigParser
from zipfile import ZipFile


_endpoint = 'http://localhost:3000'
_model_loaders = {
    'keras': _load_keras
}


class NonExistentHubItemError(Exception):
    """
    Raised when you try to load something from the hub that doesnt exist
    """

    def __init__(self, repository, item):
        super().__init__(
            f'The item "{item}" could not be found in the {repository} repository.'
        )

class InvalidMetadataError(Exception):
    """
    Raised when something from the hub doesn't have the right metadata
    """

    def __init__(self):
        super().__init__(
            f'Invalid or non-existent metadata!'
        )


def _download_and_extract(repository, item, verbose=True):
    """
    Load something from a particular repository on the hub. Returns the location of the downloaded item.
    repository              - one of 'dataset' and 'model'
    item                    - slug of item to pull
    """
    # Check if the item already exists in the cache
    cache_dir = _get_cache_dir(repository)
    item_dir = os.path.join(cache_dir, item)
    if not os.path.exists(item_dir):
        # Check if the item exists on the hub
        if not _check_exists(repository, item):
            raise NonExistentHubItemError(repository, item)
        # Download the item
        if verbose:
            print(f'Downloading "{item}" from "{repository}" repository.')
        r = requests.get(f'{_endpoint}/api/{repository}/{item}/download')
        if r.status_code == 200:
            os.mkdir(item_dir)
            archive_path = os.path.join(item_dir, f'{item}.tmp')
            with open(archive_path, 'wb+') as f:
                f.write(r.content)
                f.close()
            # Extract the item
            if verbose:
                print(f'Extracting "{item}" to "{item_dir}"')
            with ZipFile(archive_path) as zf:
                zf.extractall(item_dir)
                zf.close()
            # Remove the archive
            os.remove(archive_path)
    return item_dir


def _get_cache_dir(repository):
    cache_base = appdirs.user_cache_dir('argflow', 'argflow')
    cache_repo = os.path.join(cache_base, repository)
    # Make dirs if needed
    if not os.path.exists(cache_base):
        os.makedirs(cache_base)
    if not os.path.exists(cache_repo):
        os.mkdir(cache_repo)
    return cache_repo


def _check_exists(repository, item):
    """
    Check if an item exists on a repository on the hub.
    repository              - one of 'dataset' and 'model'
    item                    - slug/id of item to pull
    """
    r = requests.get(f'{_endpoint}/api/{repository}/{item}')
    return len(r.json()) == 1


def empty_cache():
    """
    Empties the hub cache.
    """
    cache_dir = appdirs.user_cache_dir('argflow', 'argflow')
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)


def load_model(model, verbose=True):
    """
    Load a model from the hub.
    model                   - a model slug
    """
    model_dir = _download_and_extract('model', model, verbose=verbose)
    # Load metadata
    metadata_path = os.path.join(model_dir, 'model.metadata')
    metadata = ConfigParser()
    metadata.read(metadata_path)
    try:
        model_type = metadata['GENERAL']['type']
        # Load the model
        return _model_loaders[model_type](model_dir)
    except KeyError as e:
        raise InvalidMetadataError() from e


def load_dataset(dataset, train_val_test_split=None, verbose=True):
    """
    Load a dataset from the hub with a given train-validation-test split.
    If the split is provided, returns tuple of (training set, validation set, testing set, dataset root directory).
    Otherwise, returns tuple of (data, dataset root directory)
    dataset                 - a dataset slug
    train_val_test_split    - a triple denoting the train-validation-test ratio (e.g. (70, 10, 20))
    """
    data_dir = _download_and_extract('dataset', dataset, verbose=verbose)
    # Load the dataset
    data_path = os.path.join(data_dir, 'data.h5')
    data = pd.read_hdf(data_path, 'df')
    if train_val_test_split is None:
        return data, data_dir
    assert len(train_val_test_split) == 3
    n = len(data)
    # Split the dataset into train-val-test sets
    split_ratio = [x / sum(train_val_test_split)
                   for x in train_val_test_split]
    train_size = math.floor(split_ratio[0] * n)
    val_size = math.floor(split_ratio[1] * n)
    train = data[0: train_size]
    val = data[train_size: train_size + val_size]
    test = data[train_size + val_size: n]
    return train, val, test, data_dir
