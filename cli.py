from datetime import datetime
from typing import List, Optional, Tuple

from routing import (
    load_default_graph,
    find_route,
    resolve_stop,
    parse_time_to_minutes,
    minutes_to_hhmm,
    find_nearest_stop,
)
from geocoding import geocode_address
from osm_routing import find_osm_route, RouteNotFoundError
from visualization_osmnx import save_route_map, save_coords_map


def classify_query(query: str, stop_names: List[str]) -> Tuple[Optional[str], Optional[Tuple[float, float]]]:
    """Determine whether ``query`` refers to a stop or an address.

    If ``query`` matches a known stop name (case-insensitive or with a high
    similarity cutoff), return the stop name and ``None`` for the coordinates.
    Otherwise try to geocode the query and return ``(None, (lat, lon))``.
    ``geocode_address`` may raise exceptions which the caller should handle.
    """

    # Exact match (case-insensitive) first
    stop_lookup = {name.lower(): name for name in stop_names}
    if query.lower() in stop_lookup:
        return stop_lookup[query.lower()], None

    # Fuzzy match with a higher cutoff for reliability
    stop = resolve_stop(query, stop_names, cutoff=0.85)
    if stop:
        return stop, None

    coords = geocode_address(query)
    return None, coords

def run_cli(network_type: str = "drive") -> None:
    """Interactive command line interface for different routing modes.

    ``network_type`` is used as default for car routing and map visualization.
    """

    graph = load_default_graph()
    stop_names = list(graph.nodes.keys())

    while True:
        start_query = input("Von wo? (Haltestelle oder Adresse, 'reset'/'exit'): ").strip()
        if start_query.lower() == "exit":
            break
        if start_query.lower() == "reset":
            continue

        goal_query = input("Nach wo? (Haltestelle oder Adresse, 'reset'/'exit'): ").strip()
        if goal_query.lower() == "exit":
            break
        if goal_query.lower() == "reset":
            continue

        mode = input("Verkehrsmittel [auto/rad/fuss/bahn] (or 'reset'/'exit'): ").strip().lower()
        if mode == "exit":
            break
        if mode == "reset":
            continue

        try:
            start, start_coords = classify_query(start_query, stop_names)
        except Exception as exc:
            print(f"Failed to resolve '{start_query}': {exc}")
            continue

        try:
            goal, goal_coords = classify_query(goal_query, stop_names)
        except Exception as exc:
            print(f"Failed to resolve '{goal_query}': {exc}")
            continue

        if start is not None:
            node = graph.nodes.get(start)
            if not node or node.lat is None or node.lon is None:
                print(f"No coordinates for stop '{start}'")
                continue
            start_coords = (node.lat, node.lon)

        if goal is not None:
            node = graph.nodes.get(goal)
            if not node or node.lat is None or node.lon is None:
                print(f"No coordinates for stop '{goal}'")
                continue
            goal_coords = (node.lat, node.lon)

        if mode in {"auto", "rad", "fuss"}:
            nt_map = {"auto": "drive", "rad": "bike", "fuss": "walk"}
            nt = nt_map[mode]
            try:
                coords_path = find_osm_route(
                    start_coords, goal_coords, network_type=nt
                )
            except RouteNotFoundError as exc:
                print(exc)
                continue

            print("Route coordinates:")
            for lat, lon in coords_path:
                print(f"  {lat:.5f}, {lon:.5f}")
            filename = save_coords_map(coords_path, network_type=nt)
            if filename:
                print(f"Map saved to {filename}")
            continue

        # Bahn routing with optional walking segments
        choice_time = input(
            "Zeit wählen [now/abfahrt/anreise] (or 'reset'/'exit'): "
        ).strip().lower()
        if choice_time == "exit":
            break
        if choice_time == "reset":
            continue
        if choice_time == "now":
            now = datetime.now()
            start_minutes = now.hour * 60 + now.minute + now.second / 60.0
            reverse = False
        elif choice_time == "abfahrt":
            dep_str = input("Abfahrtszeit (HH:MM) (or 'reset'/'exit'): ").strip()
            if dep_str.lower() == "exit":
                break
            if dep_str.lower() == "reset":
                continue
            start_minutes = parse_time_to_minutes(dep_str)
            reverse = False
        elif choice_time == "anreise":
            arr_str = input("Ankunftszeit (HH:MM) (or 'reset'/'exit'): ").strip()
            if arr_str.lower() == "exit":
                break
            if arr_str.lower() == "reset":
                continue
            start_minutes = parse_time_to_minutes(arr_str)
            reverse = True
        else:
            print("Ungültige Wahl, benutze aktuelle Zeit.")
            now = datetime.now()
            start_minutes = now.hour * 60 + now.minute + now.second / 60.0
            reverse = False

        choice = input(
            "Sort route by time or transfers? [time/transfers] (or 'reset'/'exit'): "
        ).strip().lower()
        if choice == "exit":
            break
        if choice == "reset":
            continue

        start_stop = start if start is not None else find_nearest_stop(graph, start_coords)
        goal_stop = goal if goal is not None else find_nearest_stop(graph, goal_coords)

        walk_start = None
        if start is None and start_stop is not None:
            node = graph.nodes.get(start_stop)
            if node and node.lat is not None and node.lon is not None:
                try:
                    walk_start = find_osm_route(
                        start_coords, (node.lat, node.lon), network_type="walk"
                    )
                except RouteNotFoundError as exc:
                    print(f"Walk to start failed: {exc}")

        walk_end = None
        if goal is None and goal_stop is not None:
            node = graph.nodes.get(goal_stop)
            if node and node.lat is not None and node.lon is not None:
                try:
                    walk_end = find_osm_route(
                        (node.lat, node.lon), goal_coords, network_type="walk"
                    )
                except RouteNotFoundError as exc:
                    print(f"Walk to destination failed: {exc}")

        if start_stop is None or goal_stop is None:
            print("Could not determine nearby stops for transit routing.")
            continue

        path = find_route(
            graph,
            start_stop,
            goal_stop,
            start_minutes,
            reverse=reverse,
            sort_by=choice,
        )

        if path:
            print("Found path:")
            start_stop_name = path[0][0]
            print(f"Start at {start_stop_name}")
            for step in path[1:]:
                if len(step) == 3:
                    stop, line, arr = step
                    line_str = line if line is not None else "start"
                    print(f"Take {line_str} to {stop} arriving at {minutes_to_hhmm(arr)}")
                else:
                    stop, line = step
                    line_str = line if line is not None else "start"
                    print(f"Take {line_str} to {stop}")

            filename = save_route_map(graph, path, network_type="walk")
            if filename:
                print(f"Map saved to {filename}")
            if walk_start:
                print("Fußweg zum Start:")
                for lat, lon in walk_start:
                    print(f"  {lat:.5f}, {lon:.5f}")
            if walk_end:
                print("Fußweg zum Ziel:")
                for lat, lon in walk_end:
                    print(f"  {lat:.5f}, {lon:.5f}")
        else:
            print("No path found.")


if __name__ == "__main__":
    run_cli()
