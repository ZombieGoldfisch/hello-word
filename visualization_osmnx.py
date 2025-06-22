from typing import List, Tuple, Optional

from graph import Graph
from routing import minutes_to_hhmm


def save_route_map(
    graph: Graph,
    path: List[Tuple[str, Optional[str], float]],
    filename: str = "route_map.html",
    network_type: str = "drive",
) -> Optional[str]:
    """Save the list of stops as an interactive HTML map using OSM data.

    Coordinates are looked up from ``graph``.  Routes between consecutive
    stops are calculated on an OpenStreetMap network.  ``network_type`` can
    be used to choose the network, e.g. ``"drive"`` or ``"walk"``.  The
    resulting HTML file is returned or ``None`` if any stop lacks coordinate
    data.
    """

    try:
        import folium
        import osmnx as ox
        import networkx as nx
    except Exception:
        print("Visualization requires 'folium' and 'osmnx'.")
        return None

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

    # Build segments along the OSM network for each pair of stops
    for i in range(len(coords) - 1):
        origin = coords[i]
        dest = coords[i + 1]
        north = max(origin[0], dest[0]) + 0.005
        south = min(origin[0], dest[0]) - 0.005
        east = max(origin[1], dest[1]) + 0.005
        west = min(origin[1], dest[1]) - 0.005
        try:
            G = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
            orig_node = ox.nearest_nodes(G, origin[1], origin[0])
            dest_node = ox.nearest_nodes(G, dest[1], dest[0])
            route = nx.shortest_path(G, orig_node, dest_node, weight="length")
            route_gdf = ox.route_to_gdf(G, route)
            route_coords = [(lat, lon) for lon, lat in route_gdf.geometry.iloc[0].coords]
            folium.PolyLine(route_coords, color="blue").add_to(m)
        except Exception:
            # Fallback to straight line if routing fails
            folium.PolyLine([origin, dest], color="blue", dash_array="5").add_to(m)

    for (step, (lat, lon)) in zip(path, coords):
        stop, line, arr = step
        popup = f"{stop} ({minutes_to_hhmm(arr)})"
        folium.Marker([lat, lon], tooltip=popup).add_to(m)

    m.save(filename)
    return filename



