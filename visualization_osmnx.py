from typing import List, Tuple, Optional

import folium

from graph import Graph
from routing import minutes_to_hhmm

def save_route_map(
    graph: Graph,
    path: List[Tuple[str, Optional[str], float]],
    filename: str = "route_map.html",
    network_type: str = "drive",
) -> Optional[str]:
    """Save the list of stops as an interactive HTML map.

    Coordinates are looked up from ``graph``.  The resulting list of
    coordinates is plotted directly without erneute Berechnung entlang des
    OSM-Netzes. ``network_type`` remains for backward compatibility but is not
    used any more. The function returns the generated HTML file or ``None`` if
    Koordinaten fehlen.
    """

    coords = []
    for step in path:
        stop = step[0]
        node = graph.nodes.get(stop)
        if not node or node.lat is None or node.lon is None:
            print(f"No coordinates for stop '{stop}'")
            return None
        coords.append((node.lat, node.lon))

    if not coords:
        return None

    m = folium.Map(location=coords[0], zoom_start=13)
    folium.PolyLine(coords, color="blue").add_to(m)

    for (step, (lat, lon)) in zip(path, coords):
        stop, line, arr = step
        popup = f"{stop} ({minutes_to_hhmm(arr)})"
        folium.Marker([lat, lon], tooltip=popup).add_to(m)

    m.save(filename)
    return filename


def save_coords_map(
    coords: List[Tuple[float, float]],
    filename: str = "osm_route_map.html",
    network_type: str = "drive",
) -> Optional[str]:
    """Save a coordinate path as an interactive HTML map.

    The provided coordinates are drawn directly as a polyline. The parameter
    ``network_type`` is kept for API compatibility but no longer influences the
    output.
    """

    if not coords:
        return None

    m = folium.Map(location=coords[0], zoom_start=13)
    folium.PolyLine(coords, color="blue").add_to(m)

    for lat, lon in coords:
        folium.Marker([lat, lon]).add_to(m)

    m.save(filename)
    return filename

