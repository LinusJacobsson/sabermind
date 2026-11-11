BASE_API_URL = "https://api2.odds-api.io/v3"
DEFAULT_TIMEOUT = 5


class Endpoints:
    """API endpoint paths."""

    GET_ARBITRAGE_BETS = "arbitrage-bets"

    GET_BOOKMAKERS = "bookmakers"
    GET_SELECTED_BOOKMAKERS = "bookmakers/selected"
    CLEAR_SELECTED_BOOKMAKERS = "bookmakers/selected/clear"
    SELECT_BOOKMAKERS = "bookmakers/selected/select"

    GET_EVENTS = "events"
    GET_LIVE_EVENTS = "events/live"
    SEARCH_EVENTS = "events/search"
    GET_EVENT_BY_ID = "events/{id}"

    GET_LEAGUES = "leagues"

    GET_EVENT_ODDS = "odds"
    GET_ODDS_MOVEMENT = "odds/movements"
    GET_ODDS_FOR_MULTIPLE_EVENTS = "odds/multi"
    GET_UPDATED_ODDS_SINCE_TIMESTAMP = "odds/updated"

    GET_PARTICIPANTS = "participants"
    GET_PARTICIPANT_BY_ID = "participants/{id}"

    GET_SPORTS = "sports"

    GET_VALUE_BETS = "value-bets"
