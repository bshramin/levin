import networkx as nx
from .router import Router


class TransparentRouter(Router):
    cache = {}  # IDEA: We can use caching for query API answers

    def __init__(self):
        pass

    def find_route(self, network, src, dst, amount, failed_edges=[]):
        graph = network.graph.copy()
        route = []
        while len(route) == 0:
            route = nx.shortest_path(graph, src, dst)
            for i in range(len(route) - 1):
                result = network.query_channel(route[i], route[i + 1])
                if result["available_sats"] < amount:
                    graph.remove_edge(route[i], route[i + 1])
                    route = []
                    continue

        return route
