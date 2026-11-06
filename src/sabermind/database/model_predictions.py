from sabermind.database.database import Database
from sabermind.schemas.schemas import ModelPrediction


class ModelPredictionRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create_model_prediction(self, model_prediction: ModelPrediction) -> None:
        query = """
        INSERT INTO model_predictions (prediction_id, player_id, team_id, prediction_date, predicted_value)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            model_prediction.prediction_id,
            model_prediction.event_id,
            model_prediction.model_name,
            model_prediction.market,
            model_prediction.outcome,
            model_prediction.predicted_probability,
        )
        self.db.execute_query(query, params)

    def get_model_prediction(self, prediction_id: str) -> ModelPrediction | None:
        query = "SELECT prediction_id, player_id, team_id, prediction_date, predicted_value FROM model_predictions WHERE prediction_id = %s"
        params = (prediction_id,)
        result = self.db.execute_query(query, params)
        if result:
            return ModelPrediction(
                prediction_id=result[0][0],
                event_id=result[0][1],
                model_name=result[0][2],
                market=result[0][3],
                outcome=result[0][4],
                predicted_probability=result[0][5],
            )
        return None
