# A quick demo using the library
from argflow import hub

hub.empty_cache()
hub.load_model('vgg16').summary()
