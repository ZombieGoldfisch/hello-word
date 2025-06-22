from datetime import datetime

from routing import (
    load_default_graph,
    find_route,
    resolve_stop,
    parse_time_to_minutes,
    minutes_to_hhmm,
)
from geocoding import geocode_address
from osm_routing import find_osm_route
from visualization_osmnx import save_route_map

def run_cli(network_type: str = "drive") -> None:
    """Interactive command line interface using :func:`find_route` or
    :func:`find_osm_route`.

    ``network_type`` specifies the OSM network used for address routing and
    map visualization.
    """

    graph = load_default_graph()
    stop_names = list(graph.nodes.keys())

    while True:
        start_query = input("Start stop or address (or 'reset'/'exit'): ").strip()
        if start_query.lower() == "exit":
            break
        if start_query.lower() == "reset":
            continue
        start = resolve_stop(start_query, stop_names)
        if start is None:
            try:
                start_coords = geocode_address(start_query)
            except Exception as exc:
                print(f"Failed to geocode '{start_query}': {exc}")
                continue
        else:
            node = graph.nodes.get(start)
            if not node or node.lat is None or node.lon is None:
                print(f"No coordinates for stop '{start}'")
                continue
            start_coords = (node.lat, node.lon)

        goal_query = input("Goal stop or address (or 'reset'/'exit'): ").strip()
        if goal_query.lower() == "exit":
            break
        if goal_query.lower() == "reset":
            continue
        goal = resolve_stop(goal_query, stop_names)
        if goal is None:
            try:
                goal_coords = geocode_address(goal_query)
            except Exception as exc:
                print(f"Failed to geocode '{goal_query}': {exc}")
                continue
        else:
            node = graph.nodes.get(goal)
            if not node or node.lat is None or node.lon is None:
                print(f"No coordinates for stop '{goal}'")
                continue
            goal_coords = (node.lat, node.lon)

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

        if start is not None and goal is not None:
            path = find_route(
                graph,
                start,
                goal,
                start_minutes,
                reverse=reverse,
                sort_by=choice,
            )

            if path:
                print("Found path:")
                start_stop = path[0][0]
                print(f"Start at {start_stop}")
                for step in path[1:]:
                    if len(step) == 3:
                        stop, line, arr = step
                        line_str = line if line is not None else "start"
                        print(
                            f"Take {line_str} to {stop} arriving at {minutes_to_hhmm(arr)}"
                        )
                    else:
                        stop, line = step
                        line_str = line if line is not None else "start"
                        print(f"Take {line_str} to {stop}")

                filename = save_route_map(graph, path, network_type=network_type)
                if filename:
                    print(f"Map saved to {filename}")
            else:
                print("No path found.")
        else:
            coords_path = find_osm_route(
                start_coords,
                goal_coords,
                network_type=network_type,
            )
            print("Route coordinates:")
            for lat, lon in coords_path:
                print(f"  {lat:.5f}, {lon:.5f}")


if __name__ == "__main__":
    run_cli()
