from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Callable, Any, Optional
import heapq

@dataclass(order=True)
class PrioritizedItem:
    priority: float
    node: Any=field(compare=False)

@dataclass
class Edge:
    target: str
    line: str
    time: float

@dataclass
class Node:
    name: str
    edges: List[Edge]

class Graph:
    """Simple graph structure to store nodes and weighted edges."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}

    def add_edge(self, source: str, target: str, line: str, time: float) -> None:
        if source not in self.nodes:
            self.nodes[source] = Node(name=source, edges=[])
        if target not in self.nodes:
            self.nodes[target] = Node(name=target, edges=[])
        self.nodes[source].edges.append(Edge(target=target, line=line, time=time))

    def neighbors(self, node: str) -> List[Edge]:
        return list(self.nodes.get(node, Node(name=node, edges=[])).edges)

def astar(
    graph: Graph,
    start: str,
    goal: str,
    heuristic: Callable[[str, str], float],
    time_weight: float = 1.0,
    transfer_penalty: float = 5.0,
) -> Optional[List[Tuple[str, Optional[str]]]]:
    """Compute shortest path using A* algorithm with line awareness.

    Args:
        graph: Graph object containing nodes and weighted edges.
        start: Node name where the route begins.
        goal: Destination node name.
        heuristic: Function estimating cost from a node to the goal.
        time_weight: Multiplier applied to the travel time of each edge.
        transfer_penalty: Additional cost when switching lines.

    Returns:
        List of tuples ``(stop, line)`` representing the path. The first
        element's line is ``None`` because no line has been taken yet. ``None``
        is returned if no path exists.
    """
    open_set: List[PrioritizedItem] = []
    start_state = (start, None)
    heapq.heappush(open_set, PrioritizedItem(priority=0, node=start_state))

    came_from: Dict[Tuple[str, Optional[str]], Optional[Tuple[str, Optional[str]]]] = {}
    g_score: Dict[Tuple[str, Optional[str]], float] = {start_state: 0}

    while open_set:
        current_state = heapq.heappop(open_set).node
        current_node, current_line = current_state
        if current_node == goal:
            path = []
            while True:
                path.append(current_state)
                prev = came_from.get(current_state)
                if prev is None:
                    break
                current_state = prev
            return list(reversed(path))

        for edge in graph.neighbors(current_node):
            neighbor_state = (edge.target, edge.line)
            transfer_cost = 0
            if current_line is not None and edge.line != current_line:
                transfer_cost = transfer_penalty

            tentative_g_score = (
                g_score[(current_node, current_line)]
                + edge.time * time_weight
                + transfer_cost
            )

            if tentative_g_score < g_score.get(neighbor_state, float("inf")):
                came_from[neighbor_state] = (current_node, current_line)
                g_score[neighbor_state] = tentative_g_score
                f_score = tentative_g_score + heuristic(edge.target, goal)
                heapq.heappush(
                    open_set,
                    PrioritizedItem(priority=f_score, node=neighbor_state),
                )

    return None

# Example heuristic: straight-line distance (requires coordinate lookup)
def null_heuristic(node: str, goal: str) -> float:
    return 0

if __name__ == "__main__":
    # Example usage with simple graph
    graph = Graph()
    graph.add_edge("Europaplatz/Postgalerie", "Mühlburger Tor", line="2", time=5)
    graph.add_edge("Europaplatz/Postgalerie", "Mühlburger Tor", line="9", time=5)
    graph.add_edge("Europaplatz/Postgalerie", "Mühlburger Tor", line="1", time=3)
    graph.add_edge("Mühlburger Tor", "Yorkstraße", line="2", time=3)
    graph.add_edge("Mühlburger Tor", "Yorkstraße", line="9", time=3)
    graph.add_edge("Europaplatz/Postgalerie", "Europaplatz", line="2", time=1)
    graph.add_edge("Europaplatz", "Europaplatz/Postgalerie", line="2", time=1)
    graph.add_edge("Europaplatz/Postgalerie", "Europaplatz", line="9", time=1)
    graph.add_edge("Europaplatz", "Europaplatz/Postgalerie", line="9", time=1)
    graph.add_edge("Europaplatz", "Karlstor", line="2", time=3)
    graph.add_edge("Karlstor", "Europaplatz", line="2", time=3)
    graph.add_edge("Europaplatz", "Karlstor", line="9", time=3)
    graph.add_edge("Karlstor", "Europaplatz", line="9", time=3)
    graph.add_edge("Yorkstraße", "Händelstraße", line="9", time=2)

    choice = input("Sort route by time or transfers? [time/transfers]: ").strip().lower()
    if choice.startswith("time"):
        time_weight = 1.0
        penalty = 0.1
    elif choice.startswith("transfers"):
        time_weight = 0.0
        penalty = 1.0
    else:
        print("Invalid choice. Defaulting to time.")
        time_weight = 1.0
        penalty = 0.1


    path = astar(
        graph,
        "Karlstor",
        "Mühlburger Tor",
        heuristic=null_heuristic,
        time_weight=time_weight,
        transfer_penalty=penalty,
    )

    print("Found path:")
    for stop, line in path:
        print(f"{stop} via {line}")