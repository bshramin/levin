import math

import networkx as nx
from random import Random
from threading import Lock
from .consts import SEED, NODES_NUM, CHANNELS_NUM, SATS_MIN, SATS_MAX, TOPOLOGY, TOPOLOGY_RANDOM, TOPOLOGY_PATH, \
    TOPOLOGY_STAR, TOPOLOGY_COMPLETE, TOPOLOGY_BALANCED_TREE, REOPEN

FULL_CHANNEL_BALANCE = "full_channel_balance"
LOCKED_SATS = "locked_sats"
AVAILABLE_SATS = "available_sats"
LOCK = "lock"


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
        self.config = network_config

    def get_total_balance(self, node):
        balance = 0
        edges = self.graph.out_edges(node)
        for edge in edges:
            balance += self.graph.get_edge_data(edge[0], edge[1])[AVAILABLE_SATS]
        return balance

    def query_channel(self, src, dst):
        self.sc.record_rtt(1)
        self.sc.record_query(1)
        edge = self.graph.get_edge_data(src, dst)
        return edge

    def execute_transaction(self, route, amount):
        self.sc.record_tx_try()
        for i in range(len(route) - 1):
            self.sc.record_rtt(3)
            edge = self.graph.get_edge_data(route[i], route[i + 1])
            if edge[AVAILABLE_SATS] < amount:
                if self.config[REOPEN] and amount < edge[FULL_CHANNEL_BALANCE] / 2:
                    reverse_of_edge = self.graph.get_edge_data(route[i + 1], route[i])
                    while edge[LOCKED_SATS] > 0 or reverse_of_edge[LOCKED_SATS] > 0:
                        pass
                    edge[LOCK].acquire()
                    reverse_of_edge[LOCK].acquire()
                    edge[AVAILABLE_SATS] = edge[FULL_CHANNEL_BALANCE] / 2
                    reverse_of_edge[AVAILABLE_SATS] = edge[FULL_CHANNEL_BALANCE] / 2
                    edge[LOCKED_SATS] = 0
                    reverse_of_edge[LOCKED_SATS] = 0
                    edge[LOCK].release()
                    reverse_of_edge[LOCK].release()
                    self.sc.record_channel_reopen()
                    self.sc.record_rtt(3)   # TODO: this is not accurate
                else:
                    for j in range(0, i):
                        self.sc.record_rtt(3)
                        edge = self.graph.get_edge_data(route[j], route[j + 1])
                        edge[LOCK].acquire()
                        edge[AVAILABLE_SATS] += amount
                        edge[LOCKED_SATS] -= amount
                        edge[LOCK].release()
                    self.sc.record_tx_fail()
                    return False, (route[i], route[i + 1])
            edge[LOCK].acquire()
            edge[AVAILABLE_SATS] -= amount
            edge[LOCKED_SATS] += amount
            edge[LOCK].release()

        for i in range(len(route) - 1):
            edge = self.graph.get_edge_data(route[i], route[i + 1])
            reverse_edge = self.graph.get_edge_data(route[i + 1], route[i])
            edge[LOCK].acquire()
            reverse_edge[LOCK].acquire()
            edge[LOCKED_SATS] -= amount
            reverse_edge[AVAILABLE_SATS] += amount
            edge[LOCK].release()
            reverse_edge[LOCK].release()

        self.sc.record_tx_success()
        return True, None

    def build_graph_from_config(self, nc):
        seed = nc[SEED]
        n = nc[NODES_NUM]
        m = nc[CHANNELS_NUM]
        sats_min = nc[SATS_MIN]
        sats_max = nc[SATS_MAX]
        topology = nc[TOPOLOGY]

        if m < n - 1:
            raise ValueError(
                "The number of channels must be at least n-1 for the graph to be connected."
            )

        i = 0
        graph = self.build_undirected_graph_with_topology(topology, n, m, seed+i)
        while not nx.is_connected(graph) or nx.number_of_selfloops(graph) != 0:
            i += 1
            graph = self.build_undirected_graph_with_topology(topology, n, m, seed+i)

        graph = self.build_directed_graph_with_channel_balances_from_undirected_graph(graph, sats_min, sats_max)

        return graph

    def build_directed_graph_with_channel_balances_from_undirected_graph(self, graph, sats_min, sats_max):
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

    def build_undirected_graph_with_topology(self, topology, n, m, seed):
        if topology == TOPOLOGY_RANDOM:
            return nx.gnm_random_graph(n, m, seed, directed=False)
        elif topology == TOPOLOGY_PATH:
            return nx.path_graph(n)
        elif topology == TOPOLOGY_STAR:
            return nx.star_graph(n-1)   # n-1 because the center node is not counted
        elif topology == TOPOLOGY_COMPLETE:
            raise NotImplementedError
        elif topology == TOPOLOGY_BALANCED_TREE:
            branching_factor = 2
            height = math.ceil(math.log2(n))
            graph = nx.balanced_tree(branching_factor, height)
            if 2**height - 1 > n:
                num_of_nodes_to_remove = 2**height - 1 - n
                leaf_nodes = [node for node in graph if nx.degree(graph, node) == 1]
                nodes_to_remove = leaf_nodes[-num_of_nodes_to_remove:]
                graph.remove_nodes_from(nodes_to_remove)
            return graph
        else:
            raise ValueError("Unknown topology: " + topology)

    def dump(self):
        self.l.log("Dumping the network:")
        self.l.log("Nodes: " + str(self.graph.nodes()))
        self.l.log("Edges: " + str(self.graph.edges(data=True)))
