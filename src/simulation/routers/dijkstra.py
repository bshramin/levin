import networkx as nx

from .router import Router
from ..network import CAPACITY, AVAILABLE_SATS


class ShortestPathRouter(Router):
    def __init__(self):
        pass

    def find_route(self, network, src, dst, amount, failed_edges=set()):
        graph = network.graph.copy()
        for error_edge in failed_edges:
            graph.remove_edge(error_edge[0], error_edge[1])

        while True:
            try:
                route = nx.shortest_path(graph, src, dst)  # route includes src and dst [src, ..., dst]
            except nx.NetworkXNoPath:
                return [], failed_edges
            if len(route) == 0:
                return [], failed_edges

            temp_route = route
            for i in range(len(temp_route) - 1):
                edge = graph.get_edge_data(temp_route[i], temp_route[i + 1])
                if edge[CAPACITY] < amount:
                    graph.remove_edge(temp_route[i], temp_route[i + 1])
                    failed_edges.add((temp_route[i], temp_route[i + 1]))
                    route = []

            # NOTE: Sender and receiver are also aware of their balances, so we can use that information
            if len(route) > 0:
                flag = False
                if graph.get_edge_data(route[0], route[1])[AVAILABLE_SATS] < amount:
                    graph.remove_edge(route[0], route[1])
                    failed_edges.add((route[0], route[1]))
                    flag = True
                if len(route) > 2 and graph.get_edge_data(route[-2], route[-1])[AVAILABLE_SATS] < amount:
                    graph.remove_edge(route[-2], route[-1])
                    failed_edges.add((route[-2], route[-1]))
                    flag = True
                if flag:
                    route = []

            if len(route) > 0:
                return route, failed_edges
