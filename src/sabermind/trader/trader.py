import os
from typing import Any

from sabermind.database.database import Database
from sabermind.database.mappings import MappingRepository
from sabermind.database.model_predictions import ModelPredictionRepository
from sabermind.database.odds import OddsRepository
from sabermind.database.players import PlayerRepository
from sabermind.database.teams import TeamRepository
from sabermind.providers.odds_api.api import OddsApiClient


class Trader:
    def __init__(
        self,
        mapping_repository: MappingRepository,
        model_predictions_repository: ModelPredictionRepository,
        odds_repository: OddsRepository,
        player_repository: PlayerRepository,
        team_repository: TeamRepository,
        odds_api_client: OddsApiClient,
    ) -> None:
        self.mapping_repository = mapping_repository
        self.model_prediction_repository = model_predictions_repository
        self.odds_repository = odds_repository
        self.player_repository = player_repository
        self.team_repository = team_repository
        self.odds_api_client = odds_api_client
        self.sport = "baseball"
        self.league = "kbo-korean"

    def fetch_events(self) -> Any:
        events = self.odds_api_client.get_events(self.sport)
        print(f"Fetched events: {events}")
        return events


def main() -> None:
    db = Database()
    trader = Trader(
        mapping_repository=MappingRepository(db=db),
        model_predictions_repository=ModelPredictionRepository(db),
        odds_repository=OddsRepository(db=db),
        player_repository=PlayerRepository(db=db),
        team_repository=TeamRepository(db=db),
        odds_api_client=OddsApiClient(ODDS_API_KEY),
    )
    trader.fetch_events()


if __name__ == "__main__":
    ODDS_API_KEY = os.getenv("API_KEY")
    main()
