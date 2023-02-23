import networkx as nx
from .router import Router


class ShortestPathRouter(Router):
    def __init__(self):
        pass

    def find_route(self, network_graph_copy, src, dst):
        return nx.shortest_path(network_graph_copy, src, dst)
