from .gaf import GAF, Payload, PayloadType
from .mappers import InfluenceMapper, CharacterisationMapper, StrengthMapper
from ..chi import Chi
from ..influence import InfluenceGraph


class GAFExtractor:
    def __init__(self, influence_mapper, strength_mapper, characterisation_mapper, chi):
        """
        influence_mapper        - a function that generates the relevant influence graph from a model given an input.
        strength_mapper         - a function that provides a strength given the source and destination of an edge.
        characterisation_mapper - a function that provides the relevant characterisation for an argument.
        chi                     - a Chi instance that generates visualisations for an argument.
        """
        super().__init__()
        assert isinstance(influence_mapper, InfluenceMapper)
        assert isinstance(strength_mapper, StrengthMapper)
        assert isinstance(characterisation_mapper, CharacterisationMapper)
        assert isinstance(chi, Chi)
        self.influence_mapper = influence_mapper
        self.strength_mapper = strength_mapper
        self.characterisation_mapper = characterisation_mapper
        self.chi = chi

    def extract(self, model, x):
        """
        Extract a GAF from a model.

        model           - a Model.
        x               - some input to the model.
        """
        influences, predicted_class, confidence = self.influence_mapper.apply(
            model, x
        )   # Assume outputs an InfluenceGraph
        gaf = GAF()
        starting, intermediate, terminal = influences.get_typed_nodes()
        # Generate GAF
        for node, data in influences.nodes().items():
            if node in starting:
                payload = Payload('Input', PayloadType.STRING)
                gaf.add_input(node,
                              payload=payload
                              )
            if node in intermediate:
                payload = self.chi.generate(x, data, model)
                gaf.add_argument(node,
                                 strength=self.strength_mapper.apply(data),
                                 payload=payload
                                 )
            if node in terminal:
                gaf.add_conclusion(node,
                                   predicted_class=predicted_class,
                                   confidence=confidence
                                   )
            for _, v, _ in influences.influences_from(node):
                gaf.add_relation(
                    node, v, self.characterisation_mapper.apply(data)
                )
        return gaf
