from typing import Protocol


class Model(Protocol):
    """Protocol for models."""

    def predict(self, *args: object, **kwargs: object) -> object:
        """Predict method to be implemented by models."""
        ...

    def train(self, *args: object, **kwargs: object) -> None:
        """Train method to be implemented by models."""
        ...

    def evaluate(self, *args: object, **kwargs: object) -> float:
        """Evaluate method to be implemented by models."""
        ...

    def save(self, *args: object, **kwargs: object) -> None:
        """Save method to be implemented by models."""
        ...
