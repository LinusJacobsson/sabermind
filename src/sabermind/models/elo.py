# www.wikipedia.org/wiki/Elo_rating_system
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInput:
    k_factor: int
    home_advantange: float
    base_rating: int
    home_elo: int
    away_elo: int
    home_score: int
    away_score: int


class EloModel:
    def __init__(self, k_factor: float = 5, home_advantage: float = 25) -> None:
        self.base_rating = 1500
        self.k_factor = k_factor
        self.home_field_advantage = home_advantage

    def predict(self, model_input: ModelInput) -> float:
        adjusted_home_elo = model_input.home_elo + self.home_field_advantage
        result = 1 / (1 + 10 ** ((model_input.away_elo - adjusted_home_elo) / 400))
        print(f"Simulation result: {result}")
        return result

    def update_ratings(self, model_input: ModelInput) -> tuple[float, float]:
        expected_home = self.predict(model_input=model_input)
        expected_away = 1 - expected_home

        actual_home = (
            1
            if model_input.home_score > model_input.away_score
            else 0
            if model_input.home_score < model_input.away_score
            else 0.5
        )
        actual_away = 1 - actual_home

        new_home_elo = model_input.home_elo + self.k_factor * (
            actual_home - expected_home
        )
        new_away_elo = model_input.away_elo + self.k_factor * (
            actual_away - expected_away
        )

        return new_home_elo, new_away_elo

    def train(self, model_input: ModelInput) -> None:
        """Train method to be implemented by models."""
        ...

    def evaluate(self, model_input: ModelInput) -> float:
        """Evaluate method to be implemented by models."""
        return 0.0

    def save(self, model_input: ModelInput) -> None:
        """Save method to be implemented by models."""
        ...
