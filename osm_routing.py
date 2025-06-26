from typing import List, Tuple

import networkx as nx
import osmnx as ox


class RouteNotFoundError(Exception):
    """Raised when no OSM route between two points can be determined."""



def find_osm_route(
    start_coords: Tuple[float, float],
    goal_coords: Tuple[float, float],
    network_type: str = "drive",
) -> List[Tuple[float, float]]:
    """Return shortest route between two coordinates using OpenStreetMap.

    ``start_coords`` and ``goal_coords`` are ``(lat, lon)`` tuples.  The
    function loads an OSM network covering both points and computes the
    shortest path by edge length.  The resulting route is returned as a list
    of ``(lat, lon)`` coordinates.
    """

    north = max(start_coords[0], goal_coords[0]) + 0.005
    south = min(start_coords[0], goal_coords[0]) - 0.005
    east = max(start_coords[1], goal_coords[1]) + 0.005
    west = min(start_coords[1], goal_coords[1]) - 0.005

    try:
        G = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
    except Exception:
        center_lat = (start_coords[0] + goal_coords[0]) / 2
        center_lon = (start_coords[1] + goal_coords[1]) / 2
        G = ox.graph_from_point((center_lat, center_lon), dist=1000, network_type=network_type)

    try:
        orig_node = ox.nearest_nodes(G, start_coords[1], start_coords[0])
        dest_node = ox.nearest_nodes(G, goal_coords[1], goal_coords[0])
        path = nx.shortest_path(G, orig_node, dest_node, weight="length")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise RouteNotFoundError("No route found between the given coordinates") from exc
    except Exception as exc:
        raise RouteNotFoundError(f"Routing failed: {exc}") from exc

    return [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
