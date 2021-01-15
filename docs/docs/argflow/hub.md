# Hub API

You can interact with the ArgHub using the Hub API.

```python
from argflow import hub
```

## Methods

### `load_model(model, verbose=True)`

Load a model from the hub. If the model cannot be found, a `NonExistentHubItemError` is thrown. If the model package is corrupted, an `InvalidMetadataError` is thrown.

- `model` - a model slug

- `verbose` - toggle verbosity (bool)

```python
from argflow import hub

# Print a summary for the VGG16 Keras model
hub.load_model('vgg16').summary()
```

### `load_dataset(dataset, train_val_test_split=None, verbose=True)`

Load a dataset from the hub with a given train-validation-test split. If the dataset cannot be found, a `NonExistentHubItemError` is thrown.


If the split is provided, returns tuple of (training set, validation set, testing set, dataset root directory).
Otherwise, returns tuple of (data, dataset root directory).

- `dataset` - a dataset slug

- `train_val_test_split` - a triple denoting the train-validation-test ratio (e.g. (70, 10, 20))

```python
from argflow import hub

# Load the MNIST dataset
data, data_dir = hub.load_dataset('mnist')
```

### `empty_cache()`
Empties the hub's cache. This removes any ArgHub models saved locally.

```python
from argflow import hub

hub.empty_cache()
```

### `package_model(model, save_dir='', model_name='model')`

Packages a model so that it can be uploaded to ArgHub.

- `model`       - the model wrapped in the relevant `argflow.Model`
- `save_dir`    - directory to save the packaged model
- `model_name`  - name of the model

```python

from argflow import hub
from argflow.models import KerasModel

from keras.applications.vgg16 import VGG16

# Create a VGG16
model = VGG16(weights='imagenet')

# Package the model
hub.package_model(KerasModel(model))
```