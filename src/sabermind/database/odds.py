from sabermind.database.database import Database
from sabermind.schemas.schemas import Odds


class OddsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_odds(self, odds: Odds) -> None:
        query = """
        INSERT INTO odds (odds_id, event_id, bookmaker, market, outcome, odds_value)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            odds.odds_id,
            odds.event_id,
            odds.bookmaker,
            odds.market,
            odds.outcome,
            odds.odds_value,
        )
        self.db.execute_query(query, params)

    def get_odds(self, odds_id: str) -> Odds | None:
        query = "SELECT odds_id, event_id, bookmaker, market, selection, odds_value FROM odds WHERE odds_id = %s"
        params = (odds_id,)
        result = self.db.execute_query(query, params)
        if result:
            return Odds(
                odds_id=result[0][0],
                event_id=result[0][1],
                bookmaker=result[0][2],
                market=result[0][3],
                outcome=result[0][4],
                odds_value=result[0][5],
            )
        return None
