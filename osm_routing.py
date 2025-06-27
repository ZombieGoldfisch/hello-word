from typing import List, Tuple, Iterable, Any

import networkx as nx
import osmnx as ox


class RouteNotFoundError(Exception):
    """Raised when no OSM route between two points can be determined."""



def _route_travel_time(G: Any, path: List[Any]) -> float:
    """Return total travel time in seconds along ``path``."""
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        edges = G.get_edge_data(u, v, default={})
        if isinstance(edges, dict):
            times = [data.get("travel_time", 0.0) for data in edges.values()]
            if times:
                total += min(times)
        else:
            total += edges.get("travel_time", 0.0)
    return total


def find_osm_route(
    start_coords: Tuple[float, float],
    goal_coords: Tuple[float, float],
    network_type: str = "drive",
) -> Tuple[List[Tuple[float, float]], float]:
    """Return fastest route and travel time between two coordinates.

    ``start_coords`` and ``goal_coords`` are ``(lat, lon)`` tuples.  The
    function loads an OSM network covering both points, enriches it with
    speed and travel time estimates and computes the fastest path between the
    two points.  The resulting route is returned as a list of ``(lat, lon)``
    coordinates together with the estimated travel time in minutes.
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

    # add speed and travel time information for each edge
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    try:
        orig_node = ox.nearest_nodes(G, start_coords[1], start_coords[0])
        dest_node = ox.nearest_nodes(G, goal_coords[1], goal_coords[0])
        path = nx.shortest_path(G, orig_node, dest_node, weight="travel_time")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise RouteNotFoundError("No route found between the given coordinates") from exc
    except Exception as exc:
        raise RouteNotFoundError(f"Routing failed: {exc}") from exc

    coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]
    # ``ox.utils_graph.get_route_edge_attributes`` was removed in older OSMnx
    # versions, so compute travel time manually to stay compatible.
    travel_seconds = _route_travel_time(G, path)
    travel_time_min = travel_seconds / 60.0
    return coords, travel_time_min
