import networkx as nx
from .router import Router
from ..network import CAPACITY


class ShortestPathRouter(Router):
    def __init__(self):
        pass

    def find_route(self, network, src, dst, amount, failed_edges=[]):
        graph = network.graph.copy()
        for error_edge in failed_edges:
            graph.remove_edge(error_edge[0], error_edge[1])

        while True:
            try:
                route = nx.shortest_path(graph, src, dst)
            except nx.NetworkXNoPath:
                return []
            if len(route) == 0:
                return []
            for i in range(len(route) - 1):
                edge = graph.get_edge_data(route[i], route[i + 1])
                if edge[CAPACITY] < amount:
                    graph.remove_edge(route[i], route[i + 1])
                    route = []
                    break
            if len(route) > 0:
                return route
