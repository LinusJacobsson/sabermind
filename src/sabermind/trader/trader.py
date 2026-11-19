import os
from typing import Any

from sabermind.database.database import Database
from sabermind.database.mappings import MappingRepository
from sabermind.database.model_predictions import ModelPredictionRepository
from sabermind.database.odds import OddsRepository
from sabermind.database.players import PlayerRepository
from sabermind.database.teams import TeamRepository
from sabermind.models.base import Model
from sabermind.models.elo import EloModel, ModelInput
from sabermind.providers.odds_api.api import OddsApiClient


class Trader[InputT]:
    def __init__(
        self,
        mapping_repository: MappingRepository,
        model_predictions_repository: ModelPredictionRepository,
        odds_repository: OddsRepository,
        player_repository: PlayerRepository,
        team_repository: TeamRepository,
        odds_api_client: OddsApiClient,
        model: Model[InputT],
    ) -> None:
        self.mapping_repository = mapping_repository
        self.model_prediction_repository = model_predictions_repository
        self.odds_repository = odds_repository
        self.player_repository = player_repository
        self.team_repository = team_repository
        self.odds_api_client = odds_api_client
        self.model = model
        self.sport = "baseball"
        self.league = "kbo-korean"

    def fetch_events(self) -> Any:
        events = self.odds_api_client.get_events(self.sport)
        # print(f"Fetched events: {events}")
        return events


def main() -> None:
    db = Database()
    model_input = ModelInput(
        k_factor=5,
        home_advantange=25,
        base_rating=1500,
        home_elo=3000,
        away_elo=3000,
        home_score=1,
        away_score=0,
    )
    trader = Trader(
        mapping_repository=MappingRepository(db=db),
        model_predictions_repository=ModelPredictionRepository(db),
        odds_repository=OddsRepository(db=db),
        player_repository=PlayerRepository(db=db),
        team_repository=TeamRepository(db=db),
        odds_api_client=OddsApiClient(ODDS_API_KEY),
        model=EloModel(),
    )
    trader.fetch_events()
    print("Running model sim")
    trader.model.predict(model_input=model_input)


if __name__ == "__main__":
    ODDS_API_KEY = os.getenv("API_KEY")
    main()
