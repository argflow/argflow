from abc import ABC, abstractmethod


class ExtractorMapper(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def apply(self, *args, **kwargs):
        pass


class InfluenceMapper(ExtractorMapper):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def apply(self, model, x):
        pass


class CharacterisationMapper(ExtractorMapper):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def apply(self, node):
        pass


class StrengthMapper(ExtractorMapper):

    def __init__(self, *args, **kwargs):
        super().__init__()

    @abstractmethod
    def apply(self, node):
        pass
