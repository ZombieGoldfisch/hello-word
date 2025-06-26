"""Helpers for converting addresses to coordinates."""

from typing import Tuple

try:  # optional dependency
    from geopy.geocoders import Nominatim
except Exception:  # pragma: no cover - geopy might not be installed
    Nominatim = None

import osmnx as ox

_VIEWBOX_KARLSRUHE = (8.2, 48.8, 8.9, 49.3)  # west, south, east, north

_geolocator = None
if Nominatim is not None:
    _geolocator = Nominatim(user_agent="routing-demo")


def geocode_address(query: str) -> Tuple[float, float]:
    """Return latitude and longitude for the given address query.

    A bounding box around the Karlsruhe district is applied to improve
    accuracy. If ``geopy`` is available, it is used with ``viewbox`` and
    ``bounded=True``. Otherwise ``osmnx.geocode`` is used as a fallback
    without a bounding box.  ``ValueError`` is raised when no result is found.
    """

    if _geolocator is not None:
        loc = _geolocator.geocode(
            query,
            viewbox=_VIEWBOX_KARLSRUHE,
            bounded=True,
        )
        if loc is None:
            raise ValueError(f"Address not found: {query}")
        return loc.latitude, loc.longitude

    if hasattr(ox, "geocode"):
        lat, lon = ox.geocode(query)
        return lat, lon

    raise RuntimeError(
        "No geocoder available (geopy or osmnx required for geocoding)"
    )
