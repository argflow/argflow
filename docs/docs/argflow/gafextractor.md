# GAFExtractor

The GAFExtractor is the driving algorithmic class of Argflow, being responsible for combining
the different modular elements of the library (argumentation frameworks, mappers and Chi) and applying
them to a given model with a specific input for generating an explanation.

### Constructor

#### `GAFExtractor(influence_mapper, strength_mapper, characterisation_mapper, chi)`

Create a GAFExtractor to which a model can be fed in order to extract an explanation based on the
mechanisms described by its arguments, which we detail below.

- `influence_mapper` - a function that generates the relevant influence graph from a model given 
  an input

- `strength_mapper` - a function that provides a strength given the source and destination of an edge
  
- `characterisation_mapper` - a function that provides the relevant characterisation for an argument

- `chi` - a Chi instance that generates visualisations for an argument

### Methods

#### `extract(self, model, x)`

This is a class method that takes a model and some input for it and returns a GAF, embellished with
the required payloads (with an inferred `PayloadType`), which can then be serialized for
communication with the Portal API, which will generatwe an explanation and the corresponding
conversational features.

- `model` - a Model.

- `x` - some input to the Model.



