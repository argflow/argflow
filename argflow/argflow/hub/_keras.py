import os


def load_keras(model_dir):
    import keras
    return keras.models.load_model(os.path.join(model_dir, 'model'))