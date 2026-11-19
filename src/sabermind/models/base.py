from typing import Protocol, TypeVar

ModelInputT = TypeVar("ModelInputT", contravariant=True)


class Model(Protocol[ModelInputT]):
    """Protocol for models."""

    def predict(self, model_input: ModelInputT) -> object:
        """Predict method to be implemented by models."""
        ...

    def train(self, model_input: ModelInputT) -> None:
        """Train method to be implemented by models."""
        ...

    def evaluate(self, model_input: ModelInputT) -> float:
        """Evaluate method to be implemented by models."""
        ...

    def save(self, model_input: ModelInputT) -> None:
        """Save method to be implemented by models."""
        ...
