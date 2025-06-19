import osmnx as ox
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

from A_Stern_Algo_3 import (
    load_default_graph,
    find_route,
    resolve_stop,
    parse_time_to_minutes,
    minutes_to_hhmm,
)


def plot_route(path: List[Tuple[str, Optional[str], float]]) -> None:
    """Plot the list of stops on an OSM map using `osmnx`.

    Each stop name is geocoded via OSM and annotated on the map.  This function
    requires network access and the ``osmnx`` package.
    """

    stops = [step[0] for step in path]
    try:
        gdf = ox.geocode_to_gdf(stops)
    except Exception as exc:
        print(f"Could not geocode stops: {exc}")
        return

    fig, ax = plt.subplots()
    gdf.plot(ax=ax, color="red")
    for idx, (step, (_, row)) in enumerate(zip(path, gdf.iterrows())):
        stop, line, arr = step
        x, y = row.geometry.x, row.geometry.y
        ax.annotate(
            f"{stop}\n{minutes_to_hhmm(arr)}",
            xy=(x, y),
            xytext=(3, 3),
            textcoords="offset points",
        )
    plt.title(f"Route from {stops[0]} to {stops[-1]}")
    plt.show()


def run_visual_cli() -> None:
    """Simple CLI that plots the computed route on a map."""

    graph = load_default_graph()
    stop_names = list(graph.nodes.keys())

    start_query = input("Start stop name: ").strip()
    start = resolve_stop(start_query, stop_names)
    if start is None:
        print(f"Unknown stop: {start_query}")
        return

    goal_query = input("Goal stop name: ").strip()
    goal = resolve_stop(goal_query, stop_names)
    if goal is None:
        print(f"Unknown stop: {goal_query}")
        return

    dep = input("Abfahrtszeit (HH:MM): ").strip()
    start_minutes = parse_time_to_minutes(dep)

    path = find_route(graph, start, goal, start_minutes)
    if not path:
        print("No path found")
        return

    for step in path[1:]:
        stop, line, arr = step
        line_str = line if line is not None else "start"
        print(f"Take {line_str} to {stop} arriving at {minutes_to_hhmm(arr)}")

    plot_route(path)


if __name__ == "__main__":
    run_visual_cli()
