import networkx as nx
from random import Random
from .consts import SEED


class Network:
    name = ""
    log_q = None
    graph = None
    rand = None

    def __init__(self, name, log_q, network_config):
        self.name = name
        self.log_q = log_q
        self.rand = Random(network_config[SEED])
        self.graph = self.build_graph_from_config(network_config)

    def build_graph_from_config(self, nc):
        n = nc["num_of_nodes"]
        m = nc["num_of_channels"]

        if m < n - 1:
            raise ValueError(
                "The number of channels must be at least n-1 for the graph to be connected."
            )

        topology = nc["topology"]
        if topology == "random":
            return self.build_random_graph(nc)
        elif topology == "star":
            raise NotImplementedError
        elif topology == "complete":
            raise NotImplementedError

    def build_random_graph(self, nc):
        seed = nc["seed"]
        n = nc["num_of_nodes"]
        m = nc["num_of_channels"]
        min_sats = nc["min_sats"]
        max_sats = nc["max_sats"]
        i = 0
        graph = nx.gnm_random_graph(n, m, seed + i, directed=False)
        while not nx.is_connected(graph) or nx.number_of_selfloops(graph) != 0:
            i += 1
            graph = gnm_random_graph(n, m, seed + i, directed=False)

        edges = graph.edges()
        graph = nx.DiGraph()
        for edge in edges:
            right_sats = self.rand.randint(min_sats, max_sats)
            left_sats = self.rand.randint(min_sats, max_sats)
            graph.add_edge(edge[0], edge[1], weight=right_sats)
            graph.add_edge(edge[1], edge[0], weight=left_sats)

        return graph

    def dump(self):
        self.log("Dumping the network:")
        self.log("Nodes: " + str(self.graph.nodes()))
        self.log("Edges: " + str(self.graph.edges(data=True)))

    def log(self, msg):
        self.log_q.put({"task": self.name, "message": msg})
