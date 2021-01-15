from abc import ABC, abstractmethod


class Chi(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self, x, node, model):
        """
        Generate a payload for a given node from a model.
        Returns a Payload.

        x           - the input in question.
        node        - the node in question.
        model       - the model in question.
        """
        pass
