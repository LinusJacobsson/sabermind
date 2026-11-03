from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field
from schemas.xid import EventId, OddsId, PlayerId, TeamId


# TODO: Add more sports as needed
class Sport(StrEnum):
    BASEBALL = "baseball"


class Team(BaseModel):
    team_id: TeamId = Field(
        ..., description="System generated unique identifier for the team."
    )
    name: str = Field(..., description="Name of the team.")
    league: str = Field(..., description="League in which the team competes.")
    sport: Sport = Field(
        Sport.BASEBALL, description="Sport in which the team competes."
    )


class Event(BaseModel):
    event_id: EventId = Field(
        ..., description="System generated unique identifier for the event."
    )
    name: str = Field(
        ..., description="Name of the event, using the format Home Team vs Away Team."
    )
    start_time: datetime = Field(
        ..., description="Start time of the event in YYYY-MM-DDTHH:MM:SS format."
    )
    location: str = Field(..., description="Location where the event takes place.")
    sport: Sport = Field(
        Sport.BASEBALL, description="Sport in which the event is held."
    )


class Player(BaseModel):
    player_id: PlayerId = Field(
        ..., description="System generated unique identifier for the player."
    )
    name: str = Field(..., description="Name of the player.")
    date_of_birth: datetime = Field(
        ..., description="Date of birth of the player in YYYY-MM-DD format."
    )
    position: str = Field(..., description="Position played by the player.")
    sport: Sport = Field(
        Sport.BASEBALL, description="Sport in which the player competes."
    )


class Odds(BaseModel):
    odds_id: OddsId = Field(
        ..., description="System generated unique identifier for the odds."
    )
    event_id: EventId = Field(
        ..., description="Identifier for the event associated with these odds."
    )
    bookmaker: str = Field(..., description="Name of the bookmaker providing the odds.")
    market: str = Field(
        ..., description="Market type for the odds (e.g., Moneyline, Spread, Total)."
    )
    outcome: str = Field(
        ...,
        description="Outcome for which the odds are provided (e.g., Team A wins, Over 2.5 goals).",
    )
    odds_value: float = Field(
        ..., description="Decimal representation of the odds value."
    )


class ModelPrediction(BaseModel):
    prediction_id: PredictionId = Field(
        ..., description="System generated unique identifier for the prediction."
    )
    event_id: EventId = Field(
        ..., description="Identifier for the event associated with this prediction."
    )
    model_name: str = Field(..., description="Name of the predictive model.")
    market: str = Field(
        ...,
        description="Market type for the prediction (e.g., Moneyline, Spread, Total).",
    )
    outcome: str = Field(
        ..., description="Predicted outcome (e.g., Team A wins, Over 2.5 goals)."
    )
    predicted_probability: float = Field(
        ...,
        description="Predicted probability of the outcome occurring (between 0 and 1).",
    )


class TeamMapping(BaseModel):
    team_id: TeamId = Field(
        ..., description="System generated unique identifier for the team."
    )
    external_team_id: str = Field(
        ..., description="External identifier for the team from a third-party source."
    )
    source: str = Field(
        ..., description="Name of the external source providing the team ID."
    )


class PlayerMapping(BaseModel):
    player_id: PlayerId = Field(
        ..., description="System generated unique identifier for the player."
    )
    external_player_id: str = Field(
        ..., description="External identifier for the player from a third-party source."
    )
    source: str = Field(
        ..., description="Name of the external source providing the player ID."
    )


class EventMapping(BaseModel):
    event_id: EventId = Field(
        ..., description="System generated unique identifier for the event."
    )
    external_event_id: str = Field(
        ..., description="External identifier for the event from a third-party source."
    )
    source: str = Field(
        ..., description="Name of the external source providing the event ID."
    )
