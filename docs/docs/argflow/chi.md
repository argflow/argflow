# Chi

Chi transforms an influence graph into a generalised argumentation framework which is given to the portal for 
generating explanations by embellishing the nodes with a `Payload`, holding metadata and the content that will 
be used in the visualisation.

### Abstract Class

In its simplest form, Chi should only provide a `generate()` function for creating payloads based on nodes.

```python
class Chi(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def generate(self, x, node, model):
        """
        Generate a payload for a given node from a model.
        Returns a Payload.

        x           - the input in question.
        node        - the node in question.
        model       - the model in question.
        """
        pass

```

### Implementation Example

Here is an example of a Chi used to generate explanations for a model 
prediction based on some input. The function `_make_actmax` returns a picture of a maximally activated
filter in the last convolutional layer of our neural network, which is simply the visual feedback of interest
in this example.

```python
class ActMax(Chi):

    def __init__(self):
        super().__init__()

    def generate(self, x, node, model):
        img_dims = (x.shape[2], x.shape[1])
        if 'layer' in node and 'filter_idx' in node:
            print(node['layer'], node['filter_idx'])
            actmax = self._make_actmax(
                x,
                model,
                node['layer'],
                node['filter_idx']
            )
            return Payload(actmax, PayloadType.IMAGE)
        return Payload(None, None)
```

### Usage and Extensibility

Chis can be implemented and extended freely as long as they are within the aforementioned constraints. 

In the
example below, notice a new Chi has been created by combining two previously created Chis, and then using
each of their respective `Payload` for a specific node to create a more complex `Payload` of type 
`IMAGE_PAIR`.

```python
from argflow.chi.cnn import GradCAM, ActMax
from argflow.chi import Chi

class GradCAMWithActMax(Chi):
    def generate(self, x, node, model):
        gc = GradCAM()
        am = ActMax()
        img_gc = gc.generate(x, node, model).content
        img_am = am.generate(x, node, model).content
        return Payload((img_gc, img_am), PayloadType.IMAGE_PAIR)
```