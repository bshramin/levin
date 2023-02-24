import networkx as nx
from random import Random
from threading import Lock
from .consts import SEED


class Network:
    name = ""
    l = None  # Logger
    sc = None  # StatCollector
    graph = None
    rand = None

    def __init__(self, name, logger, stat_collector, network_config):
        self.name = name
        self.l = logger
        self.sc = stat_collector
        self.rand = Random(network_config[SEED])
        self.graph = self.build_graph_from_config(network_config)

    def query_channel(self, src, dst):
        self.sc.record_rtt(1)
        self.sc.record_query(1)
        edge = self.graph.get_edge_data(src, dst)
        return edge

    def execute_transaction(self, route, amount):
        for i in range(len(route) - 1):
            self.sc.record_rtt(3)
            edge = self.graph.get_edge_data(route[i], route[i + 1])
            if edge["available_sats"] < amount:
                for j in range(0, i):
                    self.sc.record_rtt(3)
                    edge = self.graph.get_edge_data(route[j], route[j + 1])
                    edge["lock"].acquire()
                    edge["available_sats"] += amount
                    edge["locked_sats"] -= amount
                    edge["lock"].release()
                return False, (route[i], route[i + 1])
            edge["lock"].acquire()
            edge["available_sats"] -= amount
            edge["locked_sats"] += amount
            edge["lock"].release()

        for i in range(len(route) - 1):
            edge = self.graph.get_edge_data(route[i], route[i + 1])
            reverse_edge = self.graph.get_edge_data(route[i + 1], route[i])
            edge["lock"].acquire()
            reverse_edge["lock"].acquire()
            edge["locked_sats"] -= amount
            reverse_edge["available_sats"] += amount
            edge["lock"].release()
            reverse_edge["lock"].release()

        return True, None

    def build_graph_from_config(self, nc):
        n = nc["nodes_num"]
        m = nc["channels_num"]

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
        n = nc["nodes_num"]
        m = nc["channels_num"]
        sats_min = nc["sats_min"]
        sats_max = nc["sats_max"]
        i = 0
        graph = nx.gnm_random_graph(n, m, seed + i, directed=False)
        while not nx.is_connected(graph) or nx.number_of_selfloops(graph) != 0:
            i += 1
            graph = nx.gnm_random_graph(n, m, seed + i, directed=False)

        edges = graph.edges()
        graph = nx.DiGraph()
        for edge in edges:
            right_sats = self.rand.randint(sats_min, sats_max)
            left_sats = self.rand.randint(sats_min, sats_max)
            graph.add_edge(
                edge[0],
                edge[1],
                full_channel_balance=right_sats + left_sats,
                available_sats=right_sats,
                locked_sats=0,
                lock=Lock(),
            )
            graph.add_edge(
                edge[1],
                edge[0],
                full_channel_balance=right_sats + left_sats,
                available_sats=left_sats,
                locked_sats=0,
                lock=Lock(),
            )

        return graph

    def dump(self):
        self.l.log("Dumping the network:")
        self.l.log("Nodes: " + str(self.graph.nodes()))
        self.l.log("Edges: " + str(self.graph.edges(data=True)))
