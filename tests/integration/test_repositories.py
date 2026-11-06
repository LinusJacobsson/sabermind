import os
from collections.abc import Iterator
from datetime import date
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from sabermind.database.database import Database
from sabermind.database.mappings import MappingRepository
from sabermind.database.model_predictions import ModelPredictionRepository
from sabermind.database.odds import OddsRepository
from sabermind.database.players import PlayerRepository
from sabermind.database.teams import TeamRepository
from sabermind.schemas.schemas import (
    ModelPrediction,
    Odds,
    Player,
    PlayerMapping,
    Sport,
    Team,
)
from sabermind.schemas.xid import EventId, OddsId, PlayerId, PredictionId, TeamId, Xid

pytestmark = pytest.mark.integration
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"


@pytest.fixture
def db() -> Iterator[Database]:
    url = os.getenv("SABERMIND_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SABERMIND_TEST_DATABASE_URL to run PostgreSQL tests")
    schema = f"repository_test_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        database = Database()
        database.conn = conn
        try:
            with database.transaction():
                for path in sorted(MIGRATIONS.glob("[0-9]*.sql")):
                    conn.execute(path.read_text())
            yield database
        finally:
            conn.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def test_team_create_update_delete(db: Database) -> None:
    repo = TeamRepository(db)
    team = Team(
        team_id=TeamId(Xid.new()), name="Yankees", league="MLB", sport=Sport.BASEBALL
    )
    assert repo.get_team(str(team.team_id)) is None
    repo.create_team(team)
    assert repo.get_team(str(team.team_id)) == team
    team.name = "New York Yankees"
    repo.update_team(team)
    assert repo.get_team(str(team.team_id)) == team
    repo.delete_team(str(team.team_id))
    assert repo.get_team(str(team.team_id)) is None


def test_player_create_update_delete(db: Database) -> None:
    repo = PlayerRepository(db)
    player = Player(
        player_id=PlayerId(Xid.new()),
        name="Player",
        date_of_birth=date(1990, 1, 2),
        position="P",
        sport=Sport.BASEBALL,
    )
    assert repo.get_player(str(player.player_id)) is None
    repo.create_player(player)
    assert repo.get_player(str(player.player_id)) == player
    player.name = "Updated player"
    player.position = "C"
    repo.update_player(player)
    assert repo.get_player(str(player.player_id)) == player
    repo.delete_player(str(player.player_id))
    assert repo.get_player(str(player.player_id)) is None


def test_player_and_mapping_rollback_together(db: Database) -> None:
    players = PlayerRepository(db)
    mappings = MappingRepository(db)
    player = Player(
        player_id=PlayerId(Xid.new()),
        name="Player",
        date_of_birth=date(1990, 1, 2),
        position="P",
        sport=Sport.BASEBALL,
    )
    with pytest.raises(RuntimeError), db.transaction():
        players.create_player(player)
        mappings.create_player_mapping(
            PlayerMapping(
                player_id=player.player_id, source="provider", external_id="001"
            )
        )
        raise RuntimeError("Abort ingestion")
    assert players.get_player(str(player.player_id)) is None
    assert mappings.resolve_player("provider", "001") is None


@pytest.fixture
def event_id(db: Database) -> EventId:
    event_id = EventId(Xid.new())
    db.execute_command(
        "INSERT INTO events (event_id, name, sport, start_time, location) "
        "VALUES (%s, 'Game', 'baseball', now(), 'Park')",
        (str(event_id),),
    )
    return event_id


def test_odds_round_trip_and_event_cascade(db: Database, event_id: EventId) -> None:
    repo = OddsRepository(db)
    odds = Odds(
        odds_id=OddsId(Xid.new()),
        event_id=event_id,
        bookmaker="Bookmaker",
        market="Moneyline",
        outcome="Home",
        odds_value=1.95,
    )
    assert repo.get_odds(str(odds.odds_id)) is None
    repo.create_odds(odds)
    assert repo.get_odds(str(odds.odds_id)) == odds
    db.execute_command("DELETE FROM events WHERE event_id = %s", (str(event_id),))
    assert repo.get_odds(str(odds.odds_id)) is None


def test_prediction_round_trip_and_event_cascade(
    db: Database, event_id: EventId
) -> None:
    repo = ModelPredictionRepository(db)
    prediction = ModelPrediction(
        prediction_id=PredictionId(Xid.new()),
        event_id=event_id,
        model_name="Baseline",
        market="Moneyline",
        outcome="Home",
        predicted_probability=0.65,
    )
    assert repo.get_model_prediction(str(prediction.prediction_id)) is None
    repo.create_model_prediction(prediction)
    assert repo.get_model_prediction(str(prediction.prediction_id)) == prediction
    db.execute_command("DELETE FROM events WHERE event_id = %s", (str(event_id),))
    assert repo.get_model_prediction(str(prediction.prediction_id)) is None


def test_missing_event_is_rejected(db: Database) -> None:
    prediction = ModelPrediction(
        prediction_id=PredictionId(Xid.new()),
        event_id=EventId(Xid.new()),
        model_name="Baseline",
        market="Moneyline",
        outcome="Home",
        predicted_probability=0.65,
    )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        ModelPredictionRepository(db).create_model_prediction(prediction)
    odds = Odds(
        odds_id=OddsId(Xid.new()),
        event_id=prediction.event_id,
        bookmaker="Bookmaker",
        market="Moneyline",
        outcome="Home",
        odds_value=1.95,
    )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        OddsRepository(db).create_odds(odds)


def test_player_sport_migration_backfills_existing_rows(db: Database) -> None:
    # Recreate the pre-0008 shape and exercise the migration with an existing row.
    db.execute_command("ALTER TABLE players DROP COLUMN sport")
    player_id = PlayerId(Xid.new())
    db.execute_command(
        "INSERT INTO players (player_id, name, date_of_birth, position) "
        "VALUES (%s, 'Player', '1990-01-02', 'P')",
        (str(player_id),),
    )
    assert db.conn is not None
    with db.transaction():
        db.conn.execute((MIGRATIONS / "0008_add_player_sport.sql").read_text())
    player = PlayerRepository(db).get_player(str(player_id))
    assert player is not None
    assert player.sport == "baseball"


@pytest.mark.parametrize("probability", [-0.1, 1.1])
def test_prediction_probability_constraint(
    db: Database, event_id: EventId, probability: float
) -> None:
    prediction = ModelPrediction(
        prediction_id=PredictionId(Xid.new()),
        event_id=event_id,
        model_name="Baseline",
        market="Moneyline",
        outcome="Home",
        predicted_probability=probability,
    )
    with pytest.raises(psycopg.errors.CheckViolation):
        ModelPredictionRepository(db).create_model_prediction(prediction)
    assert (
        ModelPredictionRepository(db).get_model_prediction(
            str(prediction.prediction_id)
        )
        is None
    )
