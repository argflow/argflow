from enum import Enum
from PIL import Image


class PayloadType(str, Enum):
    STRING = 'string'
    IMAGE = 'image'
    IMAGE_PAIR = 'image_pair'


class Payload:

    def __init__(self, content, content_type):
        # Check valid payload type
        assert(type(content_type) == PayloadType)
        # Check valid payload
        if content_type == PayloadType.STRING:
            assert(isinstance(content, str))
        elif content_type == PayloadType.IMAGE:
            assert(isinstance(content, Image.Image))
        else:
            assert(isinstance(content, tuple))
        self.content_type = content_type
        self.content = content

    def __eq__(self, other):
        if isinstance(other, Payload):
            return self.content == other.content and self.content_type == other.content_type
        return False
