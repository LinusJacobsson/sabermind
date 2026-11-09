import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from sabermind.database.database import Database
from sabermind.database.exceptions import MappingConflictError
from sabermind.database.mappings import MappingRepository
from sabermind.schemas.schemas import EventMapping, Mapping, PlayerMapping, TeamMapping
from sabermind.schemas.xid import EventId, PlayerId, TeamId

pytestmark = pytest.mark.integration
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
PLAYER = PlayerId.new()
OTHER_PLAYER = PlayerId.new()
TEAM = TeamId.new()
EVENT = EventId.new()
# Historical migration fixtures deliberately use the pre-prefix ID format.
LEGACY_PLAYER = "00000000000000000000"
LEGACY_OTHER_PLAYER = "10000000000000000000"
LEGACY_TEAM = "20000000000000000000"
LEGACY_EVENT = "30000000000000000000"
LEGACY_MISSING_PLAYER = "40000000000000000000"


@pytest.fixture
def schema_db() -> Iterator[Database]:
    """Each test gets an empty schema, independent of its migration version."""
    url = os.getenv("SABERMIND_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SABERMIND_TEST_DATABASE_URL to run PostgreSQL tests")
    schema = f"mapping_test_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(schema)))
        database = Database()
        database.conn = conn
        try:
            yield database
        finally:
            conn.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def seed_entities(
    db: Database, player: str, other_player: str, team: str, event: str
) -> None:
    db.execute_command(
        "INSERT INTO players (player_id, name, date_of_birth, position) "
        "VALUES (%s, 'A', '2000-01-01', 'P'), (%s, 'B', '2000-01-01', 'P')",
        (player, other_player),
    )
    db.execute_command(
        "INSERT INTO teams (team_id, name, league, sport) "
        "VALUES (%s, 'Team', 'MLB', 'baseball')",
        (team,),
    )
    db.execute_command(
        "INSERT INTO events (event_id, name, sport, start_time, location) "
        "VALUES (%s, 'Game', 'baseball', now(), 'Park')",
        (event,),
    )


@pytest.fixture
def legacy_db(schema_db: Database) -> Database:
    """Schema immediately before 0007, with bare historical IDs."""
    assert schema_db.conn is not None
    with schema_db.transaction():
        for path in sorted(MIGRATIONS.glob("000[1-6]_*.sql")):
            schema_db.conn.execute(path.read_bytes())
        seed_entities(
            schema_db, LEGACY_PLAYER, LEGACY_OTHER_PLAYER, LEGACY_TEAM, LEGACY_EVENT
        )
    return schema_db


@pytest.fixture
def db(schema_db: Database) -> Database:
    """Current schema and prefixed IDs for repository behavior tests."""
    assert schema_db.conn is not None
    with schema_db.transaction():
        for path in sorted(MIGRATIONS.glob("[0-9]*.sql")):
            schema_db.conn.execute(path.read_bytes())
        seed_entities(schema_db, str(PLAYER), str(OTHER_PLAYER), str(TEAM), str(EVENT))
    return schema_db


def migrate(db: Database) -> None:
    assert db.conn is not None
    with db.transaction():
        db.conn.execute((MIGRATIONS / "0007_split_mappings.sql").read_bytes())


def test_migration_preserves_rows_and_timestamps(legacy_db: Database) -> None:
    db = legacy_db
    timestamp = datetime(2020, 1, 1, tzinfo=UTC)
    for kind, target in (
        ("player", LEGACY_PLAYER),
        ("team", LEGACY_TEAM),
        ("event", LEGACY_EVENT),
    ):
        db.execute_command(
            "INSERT INTO mappings "
            "(object_id, object_type, external_id, source, created_at, updated_at) "
            "VALUES (%s, %s, '001', 'provider', %s, %s)",
            (str(target), kind, timestamp, timestamp),
        )
    migrate(db)
    # The current repository expects prefixed IDs. Inspect historical rows as SQL.
    for kind, target in (
        ("player", LEGACY_PLAYER),
        ("team", LEGACY_TEAM),
        ("event", LEGACY_EVENT),
    ):
        assert db.conn is not None
        assert db.conn.execute(
            sql.SQL("SELECT source, external_id, {} FROM {}").format(
                sql.Identifier(f"{kind}_id"), sql.Identifier(f"{kind}_mappings")
            )
        ).fetchall() == [("provider", "001", target)]
    assert db.execute_query("SELECT created_at, updated_at FROM player_mappings") == [
        (timestamp, timestamp)
    ]
    assert db.execute_query("SELECT to_regclass('mappings')") == [(None,)]


@pytest.mark.parametrize(
    ("problem", "error_type"),
    [
        ("unknown_type", psycopg.errors.RaiseException),
        ("missing_target", psycopg.errors.ForeignKeyViolation),
        ("duplicate", psycopg.errors.UniqueViolation),
    ],
)
def test_invalid_legacy_data_rolls_back_entire_migration(
    legacy_db: Database, problem: str, error_type: type[psycopg.Error]
) -> None:
    db = legacy_db
    target = LEGACY_MISSING_PLAYER if problem == "missing_target" else LEGACY_PLAYER
    kind = "unsupported" if problem == "unknown_type" else "player"
    db.execute_command(
        "INSERT INTO mappings (object_id, object_type, external_id, source) "
        "VALUES (%s, %s, '001', 'provider')",
        (str(target), kind),
    )
    if problem == "duplicate":
        db.execute_command(
            "INSERT INTO mappings (object_id, object_type, external_id, source) "
            "VALUES (%s, 'player', '001', 'provider')",
            (LEGACY_OTHER_PLAYER,),
        )
    with pytest.raises(error_type):
        migrate(db)
    assert db.execute_query("SELECT count(*) FROM mappings")[0][0] >= 1
    assert db.execute_query("SELECT to_regclass('player_mappings')") == [(None,)]


@pytest.mark.parametrize(
    "mapping",
    [
        PlayerMapping(player_id=PLAYER, source="provider", external_id="001"),
        TeamMapping(team_id=TEAM, source="provider", external_id="001"),
        EventMapping(event_id=EVENT, source="provider", external_id="001"),
    ],
)
def test_mapping_round_trip_and_idempotence(db: Database, mapping: Mapping) -> None:
    repo = MappingRepository(db)
    repo.create_mapping(mapping)
    repo.create_mapping(mapping)
    if isinstance(mapping, PlayerMapping):
        assert repo.resolve_player("provider", "missing") is None
        assert repo.resolve_player("provider", "001") == PLAYER
        assert repo.list_player_mappings(PLAYER) == [mapping]
    elif isinstance(mapping, TeamMapping):
        assert repo.resolve_team("provider", "missing") is None
        assert repo.resolve_team("provider", "001") == TEAM
        assert repo.list_team_mappings(TEAM) == [mapping]
    else:
        assert repo.resolve_event("provider", "missing") is None
        assert repo.resolve_event("provider", "001") == EVENT
        assert repo.list_event_mappings(EVENT) == [mapping]


def test_multiple_providers_aliases_and_conflicting_targets(db: Database) -> None:
    repo = MappingRepository(db)
    for source, external_id in (("a", "001"), ("b", "001"), ("a", "alias")):
        repo.create_player_mapping(
            PlayerMapping(player_id=PLAYER, source=source, external_id=external_id)
        )
    assert len(repo.list_player_mappings(PLAYER)) == 3
    with pytest.raises(MappingConflictError):
        repo.create_player_mapping(
            PlayerMapping(player_id=OTHER_PLAYER, source="a", external_id="001")
        )
    assert repo.resolve_player("a", "001") == PLAYER
    # The failed write must leave the connection usable.
    assert repo.resolve_player("b", "001") == PLAYER


def test_foreign_keys_and_transaction_rollback(db: Database) -> None:
    repo = MappingRepository(db)
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        repo.create_player_mapping(
            PlayerMapping(player_id=PlayerId.new(), source="a", external_id="001")
        )
    with pytest.raises(RuntimeError), db.transaction():
        repo.create_player_mapping(
            PlayerMapping(player_id=PLAYER, source="a", external_id="001")
        )
        raise RuntimeError("Abort entity and mapping creation")
    assert repo.resolve_player("a", "001") is None
    repo.create_player_mapping(
        PlayerMapping(player_id=PLAYER, source="a", external_id="001")
    )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        db.execute_command("DELETE FROM players WHERE player_id = %s", (str(PLAYER),))


def test_database_connect_uses_url_and_persists_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    url = os.getenv("SABERMIND_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SABERMIND_TEST_DATABASE_URL to run PostgreSQL tests")
    monkeypatch.setenv("DATABASE_URL", url)
    for name in ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"):
        monkeypatch.delenv(name, raising=False)
    first, second = Database(), Database()
    first.connect()
    second.connect()
    table = f"mapping_connection_test_{uuid4().hex}"
    assert first.conn is not None
    try:
        first.conn.execute(
            sql.SQL("CREATE TABLE {} (value int)").format(sql.Identifier(table))
        )
        first.conn.execute(
            sql.SQL("INSERT INTO {} VALUES (1)").format(sql.Identifier(table))
        )
        assert second.conn is not None
        row: Any = second.conn.execute(
            sql.SQL("SELECT value FROM {}").format(sql.Identifier(table))
        ).fetchone()
        assert row == (1,)
    finally:
        first.conn.execute(
            sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table))
        )
        first.disconnect()
        second.disconnect()
