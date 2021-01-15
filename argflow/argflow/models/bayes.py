import argflow


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
