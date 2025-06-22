from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Edge:
    target: str
    line: str
    departure: float
    travel_time: float


@dataclass
class Node:
    name: str
    edges: List[Edge]
    lat: Optional[float] = None
    lon: Optional[float] = None


class Graph:
    """Simple graph structure to store nodes and weighted edges."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}

    def add_edge(
        self,
        source: str,
        target: str,
        line: str,
        departure: float,
        travel_time: float,
        source_lat: Optional[float] = None,
        source_lon: Optional[float] = None,
        target_lat: Optional[float] = None,
        target_lon: Optional[float] = None,
    ) -> None:
        if source not in self.nodes:
            self.nodes[source] = Node(name=source, edges=[], lat=source_lat, lon=source_lon)
        else:
            if source_lat is not None:
                self.nodes[source].lat = source_lat
            if source_lon is not None:
                self.nodes[source].lon = source_lon
        if target not in self.nodes:
            self.nodes[target] = Node(name=target, edges=[], lat=target_lat, lon=target_lon)
        else:
            if target_lat is not None:
                self.nodes[target].lat = target_lat
            if target_lon is not None:
                self.nodes[target].lon = target_lon
        self.nodes[source].edges.append(
            Edge(target=target, line=line, departure=departure, travel_time=travel_time)
        )

    def neighbors(self, node: str) -> List[Edge]:
        return list(self.nodes.get(node, Node(name=node, edges=[])).edges)

    def reversed(self) -> "Graph":
        """Return a new graph with all edges reversed.

        The ``departure`` of the reversed edge corresponds to the arrival time
        at the original target stop.
        """
        rev = Graph()
        for source, node in self.nodes.items():
            for edge in node.edges:
                arrival = edge.departure + edge.travel_time
                rev.add_edge(edge.target, source, edge.line, arrival, edge.travel_time)
        return rev


if __name__ == "__main__":
    # Simple smoke test when run directly
    g = Graph()
    g.add_edge("A", "B", "1", 0.0, 5.0)
    print("Graph contains:", g.nodes)
