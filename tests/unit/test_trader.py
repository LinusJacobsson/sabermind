from typing import cast
from unittest.mock import Mock, create_autospec

import pytest

from sabermind.database.mappings import MappingRepository
from sabermind.database.model_predictions import ModelPredictionRepository
from sabermind.database.odds import OddsRepository
from sabermind.database.players import PlayerRepository
from sabermind.database.teams import TeamRepository
from sabermind.models.elo import EloModel, ModelInput
from sabermind.providers.odds_api.api import OddsApiClient
from sabermind.providers.odds_api.exceptions import OddsAPIError
from sabermind.trader.trader import Trader


@pytest.fixture
def trader() -> Trader[ModelInput]:
    return Trader(
        mapping_repository=create_autospec(MappingRepository, instance=True),
        model_predictions_repository=create_autospec(
            ModelPredictionRepository, instance=True
        ),
        odds_repository=create_autospec(OddsRepository, instance=True),
        player_repository=create_autospec(PlayerRepository, instance=True),
        team_repository=create_autospec(TeamRepository, instance=True),
        model=EloModel(),
        odds_api_client=create_autospec(OddsApiClient, instance=True),
    )


def test_fetch_events_returns_api_response(trader: Trader[ModelInput]) -> None:
    events = [{"id": 123, "home": "Tigers", "away": "Bears"}]
    get_events = cast(Mock, trader.odds_api_client.get_events)
    get_events.return_value = events

    assert trader.fetch_events() is events
    get_events.assert_called_once_with("baseball")


def test_fetch_events_propagates_api_errors(trader: Trader[ModelInput]) -> None:
    get_events = cast(Mock, trader.odds_api_client.get_events)
    get_events.side_effect = OddsAPIError("API unavailable")

    with pytest.raises(OddsAPIError, match="API unavailable"):
        trader.fetch_events()
