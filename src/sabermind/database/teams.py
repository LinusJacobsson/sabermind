from sabermind.database.database import Database
from sabermind.schemas.schemas import Team
from sabermind.schemas.xid import TeamId


class TeamRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_team(self, team: Team) -> None:
        query = """
        INSERT INTO teams (team_id, name, league, sport)
        VALUES (%s, %s, %s, %s)
        """
        params = (str(team.team_id), team.name, team.league, team.sport)
        self.db.execute_command(query, params)

    def get_team(self, team_id: str) -> Team | None:
        query = "SELECT team_id, name, league, sport FROM teams WHERE team_id = %s"
        params = (team_id,)
        result = self.db.execute_query(query, params)
        if result:
            return Team(
                team_id=TeamId.parse(result[0][0]),
                name=result[0][1],
                league=result[0][2],
                sport=result[0][3],
            )
        return None

    def update_team(self, team: Team) -> None:
        query = """
        UPDATE teams
        SET name = %s, league = %s, sport = %s, updated_at = now()
        WHERE team_id = %s
        """
        params = (team.name, team.league, team.sport, str(team.team_id))
        self.db.execute_command(query, params)

    def delete_team(self, team_id: str) -> None:
        query = "DELETE FROM teams WHERE team_id = %s"
        params = (team_id,)
        self.db.execute_command(query, params)
