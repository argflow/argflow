import os
import time
import tempfile

from ..models import KerasModel

from configparser import ConfigParser
from zipfile import ZipFile


def package_model(model, save_dir='', model_name='model'):
    """
    Packages a model so that it can be uploaded to ArgHub.

    model       - the model, wrapped in the relevant argflow.Model
    save_dir    - directory to save the packaged model
    model_name  - name of the model
    """
    # Init temp dir
    temp_dir = tempfile.TemporaryDirectory()
    model_temp = os.path.join(temp_dir.name, 'model')
    meta_temp = os.path.join(temp_dir.name, 'model.metadata')
    final_zip = os.path.join(save_dir, model_name + '.zip')
    config = ConfigParser()
    # Write metadata and save model
    if type(model) == KerasModel:
        config['GENERAL'] = {
            'type': 'keras'
        }
    else:
        raise TypeError('Invalid model type.')
    model.save(model_temp)
    # Save metadata
    with open(meta_temp, 'w+') as f:
        config.write(f)
        f.close()
    # Create zip file
    with ZipFile(final_zip, 'w') as zf:
        zf.write(meta_temp, os.path.basename(meta_temp))
        for root, _, files in os.walk(model_temp):
            for f in files:
                zf.write(os.path.join(root, f), os.path.relpath(
                    os.path.join(root, f), os.path.join(model_temp, '..')))

        zf.close()
    # Remove temp dir
    temp_dir.cleanup()
