import os
import time


class Writer:
    def __init__(self, root_dir, model_name):
        """
        A class for saving GAFs for visualisation in the portal.

        root_dir            - the directory where all visualisations are saved. Don't forget to
                              point the portal to this directory too!
        model_name          - the name of the model. This will be used as the model directory name.
        """

        self.root_dir = root_dir
        self._model_dir = os.path.join(self.root_dir, model_name)
        if not os.path.exists(self._model_dir):
            # Model dir does not exist
            os.makedirs(self._model_dir)
            os.mkdir(os.path.join(self._model_dir, 'model'))

    def write_gaf(self, gaf, name=None):
        """
        Write a GAF for visualisation in the portal.

        gaf                 - the GAF to be saved.
        name                - the name of the saved GAF.
        """
        if name is None:
            name = 'explanation_' + str(time.strftime('%Y-%m-%d_%H:%M:%S'))
        # Create dir for GAF
        gaf_dir = os.path.join(self._model_dir, name)
        if os.path.exists(gaf_dir):
            raise UserWarning(
                f'A GAF is already saved under the name "{name}"!')
        else:
            os.mkdir(gaf_dir)
        # Create payloads dir
        payloads_dir = os.path.join(gaf_dir, 'payloads')
        if not os.path.exists(payloads_dir):
            os.mkdir(payloads_dir)
        # Save GAF
        payloads_dir_relative_to_root = os.path.relpath(payloads_dir, self.root_dir)
        output = gaf.serialise(root_dir=self.root_dir, payloads_dir=payloads_dir_relative_to_root)
        output_path = os.path.join(gaf_dir, 'graph.json')
        with open(output_path, 'w+') as f:
            f.write(output)
            f.close()
        return output_path
