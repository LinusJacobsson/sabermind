from sabermind.database.database import Database
from sabermind.schemas.schemas import Player


class PlayerRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_player(self, player: Player) -> None:
        query = """
        INSERT INTO players (player_id, name, date_of_birth, position, sport)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            player.player_id,
            player.name,
            player.date_of_birth,
            player.position,
            player.sport,
        )
        self.db.execute_query(query, params)

    def get_player(self, player_id: str) -> Player | None:
        query = "SELECT player_id, name, date_of_birth, position, sport FROM players WHERE player_id = %s"
        params = (player_id,)
        result = self.db.execute_query(query, params)
        if result:
            return Player(
                player_id=result[0][0],
                name=result[0][1],
                date_of_birth=result[0][2],
                position=result[0][3],
                sport=result[0][4],
            )
        return None

    def update_player(self, player: Player) -> None:
        query = """
        UPDATE players
        SET name = %s, date_of_birth = %s, position = %s, sport = %s
        WHERE player_id = %s
        """
        params = (
            player.name,
            player.date_of_birth,
            player.position,
            player.sport,
            player.player_id,
        )
        self.db.execute_query(query, params)

    def delete_player(self, player_id: str) -> None:
        query = "DELETE FROM players WHERE player_id = %s"
        params = (player_id,)
        self.db.execute_query(query, params)
