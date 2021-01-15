# Payload

Payloads define the possible content types that are going to be visualised when building an explanation. 
Payloads are required in every node of a GAF to hold information about the content and content type.

### Content Types

Payloads can represent and hold the content types:

```python
class PayloadType(str, Enum):
    STRING = 'string'
    IMAGE = 'image'
    IMAGE_PAIR = 'image_pair'
```

### Example Usage

Example for creation of payloads by the activation maximization Chi for a single GAF node, 
used in explaining a convolutional neural network prediction.

```python
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