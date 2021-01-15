from argflow import hub
from argflow.models import KerasModel

from keras.applications.vgg16 import VGG16

# Create a VGG16
model = VGG16(weights='imagenet')

# Package the model
hub.package_model(KerasModel(model))
