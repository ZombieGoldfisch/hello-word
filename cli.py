from datetime import datetime

from routing import (
    load_default_graph,
    find_route,
    resolve_stop,
    parse_time_to_minutes,
    minutes_to_hhmm,
)

from visualization_osmnx import save_route_map

def run_cli() -> None:
    """Interactive command line interface using :func:`find_route`."""

    graph = load_default_graph()
    stop_names = list(graph.nodes.keys())

    while True:
        start_query = input("Start stop name (or 'reset'/'exit'): ").strip()
        if start_query.lower() == "exit":
            break
        if start_query.lower() == "reset":
            continue
        start = resolve_stop(start_query, stop_names)
        if start is None:
            print(f"Unknown stop: {start_query}")
            continue

        goal_query = input("Goal stop name (or 'reset'/'exit'): ").strip()
        if goal_query.lower() == "exit":
            break
        if goal_query.lower() == "reset":
            continue
        goal = resolve_stop(goal_query, stop_names)
        if goal is None:
            print(f"Unknown stop: {goal_query}")
            continue

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
                    print(f"Take {line_str} to {stop} arriving at {minutes_to_hhmm(arr)}")
                else:
                    stop, line = step
                    line_str = line if line is not None else "start"
                    print(f"Take {line_str} to {stop}")

            filename = save_route_map(graph, path)
            if filename:
                print(f"Map saved to {filename}")

        else:
            print("No path found.")


if __name__ == "__main__":
    run_cli()
