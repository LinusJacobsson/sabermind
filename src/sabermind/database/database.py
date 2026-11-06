import os
from typing import Any, LiteralString

import psycopg
from psycopg.abc import Params

from sabermind.database.exceptions import ConnectionError, QueryError


class Database:
    def __init__(self) -> None:
        self.conn = None

    def connect(self) -> None:
        if self.conn is None:
            try:
                self.conn = psycopg.connect(
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
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
