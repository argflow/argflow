import os
import unittest
import tempfile

from argflow.portal import Writer
from argflow.gaf import GAF, PayloadType, Payload
from argflow.gaf.frameworks import BipolarFramework


class TestWriter(unittest.TestCase):

    def test_init(self):
        # Create a temp directory
        # Have to do this for every test or else unittest will give warnings
        temp = tempfile.TemporaryDirectory()
        # Initialise a writer
        writer = Writer(temp.name, 'muddle')
        self.assertTrue(os.path.exists(
            os.path.join(temp.name, 'muddle', 'model')))
        # Wipe the temp directory
        temp.cleanup()

    def test_overwrite_gaf(self):
        temp = tempfile.TemporaryDirectory()
        # Create a GAF
        gaf = GAF()
        gaf.add_argument(1, strength=1, payload=Payload(
            '1', PayloadType.STRING))
        gaf.add_argument(2, strength=2, payload=Payload(
            '2', PayloadType.STRING))
        gaf.add_conclusion(3, 0.5, 1)
        gaf.add_relation(1, 2, BipolarFramework.ATTACK)
        gaf.add_relation(2, 3, BipolarFramework.SUPPORT)
        # Initialise a writer
        writer = Writer(temp.name, 'muddle')
        self.assertTrue(os.path.exists(
            os.path.join(temp.name, 'muddle', 'model')))
        # Write the gaf
        writer.write_gaf(gaf)
        # Write the gaf under a different name
        writer.write_gaf(gaf, 'peter')
        # Write the gaf under the same name
        with self.assertRaises(UserWarning):
            writer.write_gaf(gaf, 'peter')
        # Wipe the temp directory
        temp.cleanup()
