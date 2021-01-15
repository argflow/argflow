# Models

Argflow provides a number of wrappers for different models. At this point
we provide support for all `Keras` models as well as for Bayesian classifier models, typically
implemented through `scikit-learn`.

This is planned to be extended to conform to all `ONNX` (Open Neural Network Exchange) models, 
the option to implement adapters for all types of models is provided.

###Abstract Class

To create a model adapter and ensure compatibility with the rest of Argflow, it is sufficient
to provide an implementation of the following abstract class:

```python
class Model(ABC):

    def __init__(self, model):
        super().__init__()
        self.model = model

    @abstractmethod
    def predict(self, x, *args, **kwargs):
        """
        Evaluate model on some input
        x       - input to model
        args    - some arguments, possibly a dict
        """
        pass

    @abstractmethod
    def save(self, path, *args, **kwargs):
        """
        Save model to some path

        x       - the path to save to
        """
        pass
```

### Keras Adapter

We require adapters for compatibility with the explanation extraction functionality of Argflow,
as well as for successful usage of the Argflow Hub API.

```python
import argflow


class KerasModel(argflow.Model):

    def __init__(self, model):
        super().__init__(model)

    def predict(self, x, args=None):
        return self.model.predict(x)

    def save(self, path):
        self.model.save(path)
```

### Bayesian Classifier Model Adapter Requirements

For creating usable adapters for bayesian classifiers, the user would need to provide to following
functionality.

```python
class BayesianClassifierModel(argflow.Model):

    def __init__(self, model):
        super().__init__(model)

    def predict(self, x, args=None):
        return self.model.predict(x)

    def predict_proba(self):
        pass

    def get_input_prior(self):
        pass

    def get_output_prior(self):
        pass

    def save(self, path):
        pass
```


