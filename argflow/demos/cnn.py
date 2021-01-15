import numpy as np

from PIL import Image
from keras.applications.vgg16 import VGG16
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input, decode_predictions

from argflow.influence import InfluenceGraph
from argflow.gaf import GAFExtractor, PayloadType, Payload
from argflow.gaf.frameworks import BipolarFramework
from argflow.gaf.default_mappers import DefaultConvolutionalInfluenceMapper, DefaultConvolutionalStrengthMapper, \
    DefaultConvolutionalCharacterisationMapper
from argflow.chi.cnn import GradCAM, ActMax
from argflow.chi import Chi
from argflow.portal import Writer


class GradCAMWithActMax(Chi):
    def generate(self, x, node, model):
        gc = GradCAM()
        am = ActMax()
        img_gc = gc.generate(x, node, model).content
        img_am = am.generate(x, node, model).content
        return Payload((img_gc, img_am), PayloadType.IMAGE_PAIR)


if __name__ == '__main__':
    model = VGG16(weights='imagenet')
    summaries = Writer('../portal/examples', 'CNN Demo')

    img_path = 'demos/tiger.jpg'
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    im = DefaultConvolutionalInfluenceMapper(3, decode_predictions)
    cm = DefaultConvolutionalCharacterisationMapper()
    sm = DefaultConvolutionalStrengthMapper()

    extractor = GAFExtractor(
        im, sm, cm, GradCAMWithActMax())
    gaf = extractor.extract(model, x)
    summaries.write_gaf(gaf)
