import os
import time
from types import TracebackType
from typing import Any, Self

import requests

from sabermind.providers.odds_api.constants import Endpoints
from sabermind.providers.odds_api.exceptions import (
    InvalidAPIKeyError,
    NotFoundError,
    OddsAPIError,
    RateLimitExceededError,
    ValidationError,
)


class OddsApiClient:
    def __init__(
        self,
        api_key: str | None,
        timeout: int = 5,
        base_url: str = "https://api2.odds-api.io/v3",
    ):
        if not api_key:
            raise ValueError("API key is required to initialize OddsApiClient.")

        self.api_key = api_key
        self.timeout = timeout
        self.base_url = base_url
        self.session = requests.Session()

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions."""
        if response.ok:
            return response.json()

        status = response.status_code

        if status == 400:
            raise ValidationError(f"Invalid request: {response.text}")
        elif status == 401:
            raise InvalidAPIKeyError("Invalid API key")
        elif status == 404:
            raise NotFoundError("Resource not found")
        elif status == 429:
            raise RateLimitExceededError(
                "Rate limit exceeded - please wait before retrying"
            )
        else:
            raise OddsAPIError(f"API error {status}: {response.text}")

    @staticmethod
    def _build_params(**kwargs: Any) -> dict[str, Any]:
        """Build parameter dictionary, excluding None values and converting bools."""
        params = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            # Convert Python bools to lowercase strings for URL params
            if isinstance(v, bool):
                params[k] = str(v).lower()
            else:
                params[k] = v
        print(f"Params used: {params}")
        return params

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Make a GET request to the API."""
        url = f"{self.base_url}/{path}"
        params = params or {}
        params["apiKey"] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise OddsAPIError(f"Request failed: {e}") from e

        return self._handle_response(response)

    def get_sports(self) -> Any:
        """
        Get all available sports.

        Returns:
            List of sports with their details

        Example:
            >>> sports = client.get_sports()
            >>> for sport in sports:
            ...     print(sport['name'])
        """
        return self._get(Endpoints.GET_SPORTS)

    def get_events(
        self,
        sport: str,
        league: str | None = None,
        participant_id: int | None = None,
        status: str | None = None,
        bookmaker: str | None = None,
    ) -> Any:
        """
        Get events with optional filters.

        Args:
            sport: Sport identifier (required)
            league: League identifier
            participant_id: Filter by participant ID
            status: Event status (e.g., "upcoming", "live", "finished")
            start: Start date/time filter (ISO 8601 format)
            end: End date/time filter (ISO 8601 format)
            bookmaker: Filter by bookmaker

        Returns:
            List of events matching the filters

        Example:
            >>> events = client.get_events(
            ...     sport="basketball",
            ...     league="usa-nba",
            ...     status="upcoming"
            ... )
        """
        params = self._build_params(
            sport=sport,
            league=league,
            participantId=participant_id,
            status=status,
            bookmaker=bookmaker,
        )

        response = self._get(Endpoints.GET_EVENTS, params)
        return response

    def get_event_by_id(self, event_id: int) -> Any:
        """
         Get a specific event by ID.

         Args:
             event_id: The event ID

        Returns:
             Event details

         Example:
             >>> event = client.get_event_by_id(event_id=12345)
        """
        path = Endpoints.GET_EVENT_BY_ID.format(id=event_id)
        return self._get(path)

    def get_live_events(self, sport: str) -> Any:
        """
        Get currently live events for a sport.

        Args:
            sport: Sport identifier

        Returns:
            List of live events

        Example:
            >>> live_events = client.get_live_events(sport="basketball")
        """
        params = self._build_params(sport=sport)
        return self._get(Endpoints.GET_LIVE_EVENTS, params)

    def get_event_odds(self, event_id: str, bookmakers: list[str]) -> Any:
        """
        Get odds for a specific event.

        Args:
            event_id: Event ID
            bookmakers: Comma-separated bookmaker slugs

        Returns:
            Odds data for the event

        Example:
            >>> odds = client.get_event_odds(
            ...     event_id="12345",
            ...     bookmakers="singbet,bet365"
            ... )
        """
        params = self._build_params(eventId=event_id, bookmakers=bookmakers)
        response = self._get(Endpoints.GET_EVENT_ODDS, params)
        print(f"Raw Odds response: {response}")
        return response

    def get_odds_for_multiple_events(self, event_ids: str, bookmakers: str) -> Any:
        """
        Get odds for multiple events at once.

        Args:
            event_ids: Comma-separated event IDs
            bookmakers: Comma-separated bookmaker slugs

        Returns:
            Odds data for multiple events

        Example:
            >>> odds = client.get_odds_for_multiple_events(
            ...     event_ids="12345,67890",
            ...     bookmakers="singbet,bet365"
            ... )
        """
        params = self._build_params(eventIds=event_ids, bookmakers=bookmakers)
        return self._get(Endpoints.GET_ODDS_FOR_MULTIPLE_EVENTS, params)

    def get_bookmakers(self) -> Any:
        """
        Get all available bookmakers.

        Returns:
            List of bookmakers with their details

        Example:
            >>> bookmakers = client.get_bookmakers()
        """
        return self._get(Endpoints.GET_BOOKMAKERS)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.close()


def main() -> None:
    API_KEY = os.getenv("ODDS_API_KEY")
    client = OddsApiClient(api_key=API_KEY)
    while True:
        print(client.get_bookmakers())
        time.sleep(5)


if __name__ == "__main__":
    main()
