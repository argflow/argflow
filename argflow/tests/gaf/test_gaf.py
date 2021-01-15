import os
import glob
import json
import tempfile
import unittest

from PIL import Image
from argflow.gaf import GAF, Payload, PayloadType, NodeType
from argflow.gaf.frameworks import BipolarFramework, SupportFramework, TripolarFramework

_resource_dir = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), '..', 'resources')


class TestGAF(unittest.TestCase):

    def test_add_argument(self):
        gaf = GAF()
        gaf.add_argument(1,
                         strength=2,
                         payload=Payload('test', PayloadType.STRING))
        gaf.add_argument(2)
        self.assertEqual(
            gaf.arguments(),
            {
                1: {'strength': 2, 'payload': Payload('test', PayloadType.STRING), 'type': NodeType.ARGUMENT},
                2: {'strength': None, 'payload': None,  'type': NodeType.ARGUMENT}
            }
        )

    def test_add_add_illegal_payloads(self):
        gaf = GAF()
        with self.assertRaises(TypeError):
            gaf.add_input(1, payload=69)
        with self.assertRaises(TypeError):
            gaf.add_argument(1, strength=1, payload=69)
        with self.assertRaises(TypeError):
            gaf.add_conclusion(1, 1, 1, payload=69)

    def test_add_relation(self):
        gaf = GAF()
        gaf.add_argument(1, strength=2)
        gaf.add_argument(2)
        gaf.add_relation(1, 2, SupportFramework.SUPPORT)
        self.assertEqual(
            gaf.relations_from(1),
            [(1, 2, {'relation': SupportFramework.SUPPORT})]
        )

    def test_add_illegal_relation(self):
        gaf = GAF()
        gaf.add_argument(1, strength=2)
        gaf.add_argument(2)
        with self.assertRaises(TypeError):
            gaf.add_relation(1, 2, 'i am illegal')

    def test_add_inconsistent_relation(self):
        gaf = GAF()
        gaf.add_argument(1, strength=2)
        gaf.add_argument(2)
        gaf.add_argument(3)
        gaf.add_relation(1, 2, TripolarFramework.SUPPORT)
        with self.assertRaises(TypeError):
            gaf.add_relation(1, 3, BipolarFramework.ATTACK)

    def test_remove_relation_framework_reset(self):
        gaf = GAF()
        gaf.add_argument(1, strength=2)
        gaf.add_argument(2)
        gaf.add_argument(3)
        gaf.add_relation(1, 2, TripolarFramework.SUPPORT)
        gaf.remove_relation(1, 2)
        gaf.add_relation(1, 3, BipolarFramework.ATTACK)
        self.assertEqual(
            gaf.relations_from(1),
            [(1, 3, {'relation': BipolarFramework.ATTACK})]
        )

    def test_overwrite_relation(self):
        gaf = GAF()
        gaf.add_argument(1, strength=2)
        gaf.add_argument(2)
        gaf.add_relation(1, 2, BipolarFramework.SUPPORT)
        gaf.add_relation(1, 2, BipolarFramework.ATTACK)
        self.assertEqual(
            gaf.relations_from(1),
            [(1, 2, {'relation': BipolarFramework.ATTACK})]
        )

    def test_remove_node(self):
        gaf = GAF()
        gaf.add_argument(1, strength=2)
        gaf.add_argument(2)
        gaf.remove_node(2)
        self.assertEqual(
            gaf.arguments(),
            {
                1: {'strength': 2, 'payload': None, 'type': NodeType.ARGUMENT}
            }
        )

    def test_create_image_payload(self):
        temp = tempfile.TemporaryDirectory()
        gaf = GAF()
        img = Image.open(os.path.join(
            _resource_dir, 'test.png')).convert('RGB')
        save_path = gaf._create_payload(
            Payload(img, PayloadType.IMAGE), temp.name, '')
        generated_payloads = glob.glob(os.path.join(temp.name, '*.jpg'))
        self.assertEqual(len(generated_payloads), 1)
        self.assertEqual(os.path.basename(save_path),
                         os.path.basename(generated_payloads[0]))
        temp.cleanup()

    def test_create_image_pair_payload(self):
        temp = tempfile.TemporaryDirectory()
        gaf = GAF()
        img = Image.open(os.path.join(
            _resource_dir, 'test.png')).convert('RGB')
        _ = gaf._create_payload(
            Payload((img, img), PayloadType.IMAGE_PAIR), temp.name, '')
        generated_payloads = glob.glob(os.path.join(temp.name, '*.jpg'))
        self.assertEqual(len(generated_payloads), 2)
        temp.cleanup()

    def test_create_invalid_payload(self):
        gaf = GAF()
        with self.assertRaises(TypeError):
            gaf._create_payload('not a payload', '', '')

    def test_serialise(self):
        gaf = GAF()
        gaf.add_argument(1, strength=1, payload=Payload(
            '1', PayloadType.STRING))
        gaf.add_argument(2, strength=2, payload=Payload(
            '2', PayloadType.STRING))
        gaf.add_conclusion(3, 0.5, 1)
        gaf.add_relation(1, 2, BipolarFramework.ATTACK)
        gaf.add_relation(2, 3, BipolarFramework.SUPPORT)
        decoder = json.decoder.JSONDecoder()
        with open(os.path.join(_resource_dir, 'basic_gaf.json'), 'r') as f:
            self.assertEqual(
                decoder.decode(gaf.serialise()),
                decoder.decode(f.read())
            )
            f.close()

    def test_serialise_2(self):
        gaf = GAF()
        gaf.add_input('picture of carrot', payload=Payload(
            'picture', PayloadType.STRING))
        gaf.add_argument('orange', strength=1, payload=Payload(
            'orange body', PayloadType.STRING))
        gaf.add_argument('green', strength=2, payload=Payload(
            'green leaves', PayloadType.STRING))
        gaf.add_conclusion('carrot', 0.5, 1)
        gaf.add_relation('picture of carrot', 'orange',
                         BipolarFramework.ATTACK)
        gaf.add_relation('picture of carrot', 'green',
                         BipolarFramework.SUPPORT)
        gaf.add_relation('green', 'carrot', BipolarFramework.ATTACK)
        gaf.add_relation('orange', 'carrot', BipolarFramework.SUPPORT)
        decoder = json.decoder.JSONDecoder()
        with open(os.path.join(_resource_dir, 'carrot_gaf.json'), 'r') as f:
            self.assertEqual(
                decoder.decode(gaf.serialise()),
                decoder.decode(f.read())
            )
            f.close()
