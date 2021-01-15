from abc import ABC, abstractmethod


class ExplanationGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        resource_path: str,
        model_name: str,
        model_input: str,
        explanation_name: str,
        chi_value: str,
    ):
        pass
