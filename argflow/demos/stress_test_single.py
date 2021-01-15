import random

from argflow.gaf import GAF, Payload, PayloadType
from argflow.gaf.frameworks import BipolarFramework
from argflow.gaf.mappers import InfluenceMapper, CharacterisationMapper, StrengthMapper
from argflow.portal import Writer
from argflow.chi import Chi


FIRST = range(1, 4000)

if __name__ == '__main__':

    gaf = GAF()
    # Add start and finish
    gaf.add_input(0, payload=Payload('Input', PayloadType.STRING))
    gaf.add_conclusion(-1, 0.8, 'True', payload=Payload('Conclusion', PayloadType.STRING))
    # First layer
    for i in FIRST:
        gaf.add_argument(i, strength=random.random(), payload=Payload(
            str(i), PayloadType.STRING))
        relation = BipolarFramework.SUPPORT if random.random() < 0.8 else BipolarFramework.ATTACK
        # Connect to input
        gaf.add_relation(0, i, relation)
        gaf.add_relation(i, -1, relation)
        

    # Write explanation
    summaries = Writer('../portal/examples', 'Stress Tests')
    summaries.write_gaf(gaf)