from typing import Tuple

import osmnx as ox


def geocode_address(query: str) -> Tuple[float, float]:
    """Return latitude and longitude for the given address query.

    This function uses :func:`osmnx.geocode` to look up the coordinates and
    returns them as a ``(lat, lon)`` tuple.
    """
    lat, lon = ox.geocode(query)
    return lat, lon
