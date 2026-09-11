import os

import requests
from dotenv import load_dotenv

# Get the directory where this Python file is located.
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# Load the .env file located inside the backend folder.
ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

# Load environment variables from the .env file
load_dotenv()


# MapQuest Directions API endpoint
MAPQUEST_URL = (
    "https://www.mapquestapi.com/"
    "directions/v2/route"
)

# Maximum time to wait for a response from MapQuest
REQUEST_TIMEOUT = 10


class MapQuestError(Exception):
    """
    Custom error for problems encountered
    while communicating with MapQuest.
    """


def get_route(start, destination, unit="m"):
    """
    Request route information from MapQuest.

    Args:
        start (str): Starting location.
        destination (str): Destination location.
        unit (str): Distance unit.
                    'm' = miles
                    'k' = kilometers

    Returns:
        dict: Route information returned by MapQuest.

    Raises:
        ValueError: If the API key or input is invalid.
        MapQuestError: If the MapQuest request fails.
    """

    # Get the API key from the environment
    # instead of storing it directly in the code.
    api_key = os.getenv("MAPQUEST_API_KEY")

    if not api_key:
        raise ValueError(
            "MapQuest API key is not configured."
        )

    # Check that both locations were provided.
    if not start or not destination:
        raise ValueError(
            "Starting location and destination "
            "are required."
        )

    # Only allow the distance units supported
    # by the application.
    if unit not in ("m", "k"):
        raise ValueError(
            "Unit must be 'm' for miles or "
            "'k' for kilometers."
        )

    # Parameters sent to the MapQuest API.
    params = {
        "key": api_key,
        "from": start,
        "to": destination,
        "unit": unit,
        "outFormat": "json"
    }

    try:
        # Send the route request to MapQuest.
        response = requests.get(
            MAPQUEST_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        # Raise an error if MapQuest returns
        # an unsuccessful HTTP status.
        response.raise_for_status()

    except requests.exceptions.Timeout as error:
        # Handle requests that take too long.
        raise MapQuestError(
            "The MapQuest request timed out."
        ) from error

    except requests.exceptions.ConnectionError as error:
        # Handle connection problems.
        raise MapQuestError(
            "Could not connect to MapQuest."
        ) from error

    except requests.exceptions.HTTPError as error:
        # Handle HTTP errors returned by the server.
        raise MapQuestError(
            "MapQuest returned an HTTP error."
        ) from error

    except requests.exceptions.RequestException as error:
        # Handle other request-related errors.
        raise MapQuestError(
            "An error occurred while contacting MapQuest."
        ) from error

    try:
        # Convert the API response from JSON
        # into a Python dictionary.
        data = response.json()

    except ValueError as error:
        # Handle responses that are not valid JSON.
        raise MapQuestError(
            "MapQuest returned an invalid response."
        ) from error

    # Get the route information from the response.
    route = data.get("route", {})

    # Check if MapQuest reported a route error.
    route_error = route.get(
        "routeError",
        {}
    )

    if route_error.get("errorCode", 0) != 0:
        raise MapQuestError(
            route_error.get(
                "message",
                "MapQuest could not calculate the route."
            )
        )

    # Return the complete route data to app.py.
    return data