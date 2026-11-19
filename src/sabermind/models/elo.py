# www.wikipedia.org/wiki/Elo_rating_system


class EloModel:
    def __init__(self, k_factor: float = 5, home_advantage: float = 25) -> None:
        self.base_rating = 1500
        self.k_factor = k_factor
        self.home_field_advantage = home_advantage

    def predict(self, home_elo: float, away_elo: float) -> float:
        adjusted_home_elo = home_elo + self.home_field_advantage
        return 1 / (1 + 10 ** ((away_elo - adjusted_home_elo) / 400))

    def update_ratings(
        self, home_elo: float, away_elo: float, home_score: int, away_score: int
    ) -> tuple[float, float]:
        expected_home = self.predict(home_elo, away_elo)
        expected_away = 1 - expected_home

        actual_home = (
            1 if home_score > away_score else 0 if home_score < away_score else 0.5
        )
        actual_away = 1 - actual_home

        new_home_elo = home_elo + self.k_factor * (actual_home - expected_home)
        new_away_elo = away_elo + self.k_factor * (actual_away - expected_away)

        return new_home_elo, new_away_elo
