from typing import LiteralString

from sabermind.database.database import Database
from sabermind.database.exceptions import MappingConflictError
from sabermind.schemas.schemas import EventMapping, Mapping, PlayerMapping, TeamMapping
from sabermind.schemas.xid import EventId, PlayerId, TeamId, Xid


class MappingRepository:
    """Resolve provider identities without implicitly remapping existing identities."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def create_mapping(self, mapping: Mapping) -> None:
        if isinstance(mapping, PlayerMapping):
            self.create_player_mapping(mapping)
        elif isinstance(mapping, TeamMapping):
            self.create_team_mapping(mapping)
        else:
            self.create_event_mapping(mapping)

    def _create(
        self, query: LiteralString, source: str, external_id: str, target: Xid
    ) -> None:
        with self.db.transaction():
            result = self.db.execute_query(query, (source, external_id, str(target)))
            if not result:
                raise MappingConflictError(
                    f"External identity {source!r}/{external_id!r} already has "
                    "a different internal target."
                )

    def create_player_mapping(self, mapping: PlayerMapping) -> None:
        self._create(
            """
            INSERT INTO player_mappings (source, external_id, player_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (source, external_id) DO UPDATE
            SET player_id = EXCLUDED.player_id
            WHERE player_mappings.player_id = EXCLUDED.player_id
            RETURNING player_id
            """,
            mapping.source,
            mapping.external_id,
            mapping.player_id,
        )

    def create_team_mapping(self, mapping: TeamMapping) -> None:
        self._create(
            """
            INSERT INTO team_mappings (source, external_id, team_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (source, external_id) DO UPDATE
            SET team_id = EXCLUDED.team_id
            WHERE team_mappings.team_id = EXCLUDED.team_id
            RETURNING team_id
            """,
            mapping.source,
            mapping.external_id,
            mapping.team_id,
        )

    def create_event_mapping(self, mapping: EventMapping) -> None:
        self._create(
            """
            INSERT INTO event_mappings (source, external_id, event_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (source, external_id) DO UPDATE
            SET event_id = EXCLUDED.event_id
            WHERE event_mappings.event_id = EXCLUDED.event_id
            RETURNING event_id
            """,
            mapping.source,
            mapping.external_id,
            mapping.event_id,
        )

    def resolve_player(self, source: str, external_id: str) -> PlayerId | None:
        rows = self.db.execute_query(
            "SELECT player_id FROM player_mappings WHERE source = %s AND external_id = %s",
            (source, external_id),
        )
        return PlayerId.parse(rows[0][0]) if rows else None

    def resolve_team(self, source: str, external_id: str) -> TeamId | None:
        rows = self.db.execute_query(
            "SELECT team_id FROM team_mappings WHERE source = %s AND external_id = %s",
            (source, external_id),
        )
        return TeamId.parse(rows[0][0]) if rows else None

    def resolve_event(self, source: str, external_id: str) -> EventId | None:
        rows = self.db.execute_query(
            "SELECT event_id FROM event_mappings WHERE source = %s AND external_id = %s",
            (source, external_id),
        )
        return EventId.parse(rows[0][0]) if rows else None

    def list_player_mappings(self, player_id: PlayerId) -> list[PlayerMapping]:
        rows = self.db.execute_query(
            """
            SELECT source, external_id FROM player_mappings
            WHERE player_id = %s ORDER BY source, external_id
            """,
            (str(player_id),),
        )
        return [
            PlayerMapping(player_id=player_id, source=source, external_id=external_id)
            for source, external_id in rows
        ]

    def list_team_mappings(self, team_id: TeamId) -> list[TeamMapping]:
        rows = self.db.execute_query(
            """
            SELECT source, external_id FROM team_mappings
            WHERE team_id = %s ORDER BY source, external_id
            """,
            (str(team_id),),
        )
        return [
            TeamMapping(team_id=team_id, source=source, external_id=external_id)
            for source, external_id in rows
        ]

    def list_event_mappings(self, event_id: EventId) -> list[EventMapping]:
        rows = self.db.execute_query(
            """
            SELECT source, external_id FROM event_mappings
            WHERE event_id = %s ORDER BY source, external_id
            """,
            (str(event_id),),
        )
        return [
            EventMapping(event_id=event_id, source=source, external_id=external_id)
            for source, external_id in rows
        ]
