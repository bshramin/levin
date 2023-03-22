import networkx as nx
from .router import Router


class TransparentRouter(Router):
    tx_max_query_per_tx_try = -1
    cache = {}  # IDEA: We can use caching for query API answers


    def __init__(self, tx_max_query_per_tx_try):
        self.tx_max_query_per_tx_try = tx_max_query_per_tx_try

    def find_route(self, network, src, dst, amount, failed_edges=[]):
        graph = network.graph.copy()
        num_of_queries = 0

        while True:
            try:
                route = nx.shortest_path(graph, src, dst)
            except nx.NetworkXNoPath:
                return []
            if len(route) == 0:
                return []
            for i in range(len(route) - 1):
                if num_of_queries >= self.tx_max_query_per_tx_try:
                    return []
                num_of_queries += 1
                edge = network.query_channel(route[i], route[i + 1])
                if edge["available_sats"] < amount:
                    graph.remove_edge(route[i], route[i + 1])
                    route = []
                    break
            if len(route) > 0:
                return route
