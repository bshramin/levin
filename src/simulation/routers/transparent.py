import networkx as nx
from .router import Router
from ..network import CAPACITY


class TransparentRouter(Router):
    tx_max_query_per_tx_try = -1
    cache = {}  # IDEA: We can use caching for query API answers

    def __init__(self, tx_max_query_per_tx_try):
        self.tx_max_query_per_tx_try = tx_max_query_per_tx_try

    def find_route(self, network, src, dst, amount, failed_edges=[]):
        graph = network.graph.copy()
        for error_edge in failed_edges:
            graph.remove_edge(error_edge[0], error_edge[1])
        num_of_queries = 0

        while True:
            try:
                route = nx.shortest_path(graph, src, dst)
            except nx.NetworkXNoPath:
                return [], failed_edges
            if len(route) == 0:
                return [], failed_edges

            temp_route = route
            for i in range(len(temp_route) - 1):
                edge = graph.get_edge_data(temp_route[i], temp_route[i + 1])
                if edge[CAPACITY] < amount:
                    graph.remove_edge(temp_route[i], temp_route[i + 1])
                    failed_edges.append([temp_route[i], temp_route[i + 1]])
                    route = []

            if len(route) == 0:
                continue

            # TODO: we can only query the channels that have a probability of success less than a certain percentage

            num_of_queries += len(route)
            if num_of_queries >= self.tx_max_query_per_tx_try:
                return [], failed_edges

            temp_route = route
            edges = network.query_channels([[route[i], route[i + 1]] for i in range(len(route)-1)])
            for i in range(len(edges)):
                if edges[i]["available_sats"] < amount:
                    graph.remove_edge(temp_route[i], temp_route[i + 1])
                    failed_edges.append([temp_route[i], temp_route[i + 1]])
                    route = []

            if len(route) > 0:
                return route, failed_edges
