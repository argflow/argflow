# Argumentation Framework

Argumentation frameworks define the possible relations between the arguments. We provide a number of argumentation frameworks by default, all inheriting from the abstract `Framework` class (which is basically just a glorified enum).

## Support
```python
from argflow.gaf.frameworks import SupportFramework

relations = list(map(str, SupportFramework))
print(relations) # ['SupportFramework.SUPPORT']
```

## Bipolar
```python
from argflow.gaf.frameworks import BipolarFramework

relations = list(map(str, BipolarFramework))
print(relations) # ['BipolarFramework.SUPPORT', 'BipolarFramework.ATTACK']
```

## Tripolar
```python
from argflow.gaf.frameworks import TripolarFramework

relations = list(map(str, TripolarFramework))
print(relations) # ['TripolarFramework.SUPPORT', 'TripolarFramework.ATTACK', 'TripolarFramework.CRITICAL_SUPPORT']
```
