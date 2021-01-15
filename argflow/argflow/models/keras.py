import argflow


class KerasModel(argflow.Model):

    def __init__(self, model):
        super().__init__(model)

    def predict(self, x, args=None):
        return self.model.predict(x)

    def save(self, path):
        self.model.save(path)
