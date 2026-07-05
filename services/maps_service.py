"""Google Maps integration for real distance lookups used by the
transportation guardrail. Falls back gracefully when no API key is set."""
import requests

from config.settings import settings

DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def get_distance_km(origin: str, destination: str) -> float | None:
    """Returns driving distance in km between two place names, or None if the
    Google Maps API key is not configured or the lookup fails."""
    if not settings.google_maps_api_key or not origin or not destination:
        return None
    try:
        response = requests.get(
            DISTANCE_MATRIX_URL,
            params={
                "origins": origin,
                "destinations": destination,
                "key": settings.google_maps_api_key,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            return None
        return element["distance"]["value"] / 1000
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None
