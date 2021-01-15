from abc import ABC, abstractmethod


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