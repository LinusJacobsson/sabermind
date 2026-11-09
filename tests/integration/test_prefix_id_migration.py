"""Test the database format change independently of Python ID implementations."""

import os
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

pytestmark = pytest.mark.integration
MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
SUFFIX = "00000000000000000000"


@pytest.fixture
def conn() -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    url = os.getenv("SABERMIND_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set SABERMIND_TEST_DATABASE_URL to run PostgreSQL tests")
    schema = f"prefix_test_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        connection.execute(
            sql.SQL("SET search_path TO {}").format(sql.Identifier(schema))
        )
        try:
            with connection.transaction():
                for path in sorted(MIGRATIONS.glob("000[1-8]_*.sql")):
                    connection.execute(path.read_text())
            yield connection
        finally:
            connection.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema))
            )


def test_prefix_migration_preserves_entities_and_relationships(
    conn: psycopg.Connection[tuple[object, ...]],
) -> None:
    conn.execute(
        "INSERT INTO teams (team_id, name, league, sport) "
        "VALUES (%s, 'Team', 'MLB', 'baseball')",
        (SUFFIX,),
    )
    conn.execute(
        "INSERT INTO players (player_id, name, date_of_birth, position) "
        "VALUES (%s, 'Player', '1990-01-01', 'P')",
        (SUFFIX,),
    )
    conn.execute(
        "INSERT INTO events (event_id, name, sport, start_time, location) "
        "VALUES (%s, 'Game', 'baseball', now(), 'Park')",
        (SUFFIX,),
    )
    conn.execute(
        "INSERT INTO odds (odds_id, event_id, bookmaker, market_type, outcome, odds_value) "
        "VALUES (%s, %s, 'Book', 'Moneyline', 'Home', 1.95)",
        (SUFFIX, SUFFIX),
    )
    conn.execute(
        "INSERT INTO model_predictions "
        "(prediction_id, event_id, model_name, market, outcome, predicted_probability) "
        "VALUES (%s, %s, 'Baseline', 'Moneyline', 'Home', 0.65)",
        (SUFFIX, SUFFIX),
    )
    for entity in ("team", "player", "event"):
        conn.execute(
            sql.SQL(
                "INSERT INTO {} (source, external_id, {}) VALUES ('provider', '001', %s)"
            ).format(
                sql.Identifier(f"{entity}_mappings"), sql.Identifier(f"{entity}_id")
            ),
            (SUFFIX,),
        )
    before = conn.execute("SELECT created_at, updated_at FROM teams").fetchone()
    with conn.transaction():
        conn.execute((MIGRATIONS / "0009_prefix_entity_ids.sql").read_text())
    for entity in ("team", "player", "event"):
        assert conn.execute(
            sql.SQL("SELECT source, external_id, {} FROM {}").format(
                sql.Identifier(f"{entity}_id"), sql.Identifier(f"{entity}_mappings")
            )
        ).fetchone() == ("provider", "001", f"{entity}_{SUFFIX}")
    assert conn.execute("SELECT odds_id, event_id FROM odds").fetchone() == (
        f"odds_{SUFFIX}",
        f"event_{SUFFIX}",
    )
    assert conn.execute(
        "SELECT prediction_id, event_id FROM model_predictions"
    ).fetchone() == (
        f"sim_{SUFFIX}",
        f"event_{SUFFIX}",
    )
    assert conn.execute("SELECT created_at, updated_at FROM teams").fetchone() == before
    for value in (SUFFIX, f"player_{SUFFIX}", "team_invalid"):
        with pytest.raises(psycopg.errors.CheckViolation):
            conn.execute(
                "INSERT INTO teams (team_id, name, league, sport) "
                "VALUES (%s, 'Other', 'MLB', 'baseball')",
                (value,),
            )
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        conn.execute("DELETE FROM events")
    conn.execute("DELETE FROM event_mappings")
    conn.execute("DELETE FROM events")
    assert conn.execute("SELECT count(*) FROM odds").fetchone() == (0,)
    assert conn.execute("SELECT count(*) FROM model_predictions").fetchone() == (0,)


def test_prefix_migration_handles_empty_database(
    conn: psycopg.Connection[tuple[object, ...]],
) -> None:
    with conn.transaction():
        conn.execute((MIGRATIONS / "0009_prefix_entity_ids.sql").read_text())
    conn.execute(
        "INSERT INTO teams (team_id, name, league, sport) "
        "VALUES (%s, 'Team', 'MLB', 'baseball')",
        (f"team_{SUFFIX}",),
    )
    assert conn.execute("SELECT team_id FROM teams").fetchone() == (f"team_{SUFFIX}",)
