import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, LiteralString

import psycopg
from psycopg.abc import Params

from sabermind.database.exceptions import ConnectionError, QueryError


class Database:
    def __init__(self) -> None:
        self.conn: psycopg.Connection[tuple[Any, ...]] | None = None

    def connect(self) -> None:
        if self.conn is None:
            try:
                self.conn = psycopg.connect(
                    os.getenv("DATABASE_URL", ""),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    autocommit=True,
                )
            except psycopg.OperationalError as e:
                raise ConnectionError(f"Failed to connect to the database: {e}") from e

    def disconnect(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def execute_query(
        self,
        query: LiteralString,
        params: Params | None = None,
    ) -> list[tuple[Any, ...]]:
        if self.conn is None:
            raise QueryError("Database connection is not established.")

        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Commit a group of operations together, or roll back on failure."""
        if self.conn is None:
            raise QueryError("Database connection is not established.")
        with self.conn.transaction():
            yield

    def execute_command(
        self, query: LiteralString, params: Params | None = None
    ) -> None:
        """Execute a statement that does not return rows."""
        if self.conn is None:
            raise QueryError("Database connection is not established.")
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
