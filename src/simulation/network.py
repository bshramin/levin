import json
import math
import statistics
import time
from random import Random
from threading import Lock

import networkx as nx

from .consts import SEED, NODES_NUM, CHANNELS_NUM, SATS_MIN, SATS_MAX, TOPOLOGY, TOPOLOGY_RANDOM, TOPOLOGY_PATH, \
    TOPOLOGY_STAR, TOPOLOGY_COMPLETE, TOPOLOGY_BALANCED_TREE, REOPEN_ENABLED, COUNT_INITIAL_CHANNELS_AS_REOPENS, \
    DELAY_ENABLED, \
    RTT_DELAY, TX_HOP_RTTS, QUERY_RTTS, DELAY_RANDOMNESS_THRESHOLD, TOPOLOGY_FILE, TOPOLOGY_FROM_FILE, \
    OVERWRITE_BALANCES, CAPACITY_DISTRIBUTION, DISTRIBUTION_HALF, DISTRIBUTION_RANDOM, SATURATION_PROBABILITY

CAPACITY = "capacity"
LOCKED_SATS = "locked_sats"
AVAILABLE_SATS = "available_sats"
LOCK = "lock"


class Network:
    name = ""
    l = None  # Logger
    sc = None  # StatCollector
    graph = None
    rand = None
    transactions_routed_from_last_reopen = 0
    query_rtts = 0
    tx_hop_rtts = 0
    hop_delay = 0
    query_delay = 0
    delay_randomness_threshold = 0

    def __init__(self, name, logger, stat_collector, network_config):
        self.name = name
        self.l = logger
        self.sc = stat_collector
        self.rand = Random(network_config[SEED])
        self.config = network_config
        self.graph = self.build_graph_from_config()
        self.dump_graph_metrics()
        self.transactions_routed_from_last_reopen = 0
        self.query_rtts = self.config[QUERY_RTTS]
        self.tx_hop_rtts = self.config[TX_HOP_RTTS]
        self.delay_randomness_threshold = self.config[DELAY_RANDOMNESS_THRESHOLD]
        if self.config[DELAY_ENABLED]:
            self.hop_delay = self.config[RTT_DELAY] * self.tx_hop_rtts / 1000
            self.query_delay = self.config[RTT_DELAY] * self.query_rtts / 1000

    def get_total_balance(self, node):
        balance = 0
        edges = self.graph.out_edges(node)
        for edge in edges:
            balance += self.graph.get_edge_data(edge[0], edge[1])[AVAILABLE_SATS]
        return balance

    def get_max_available_out_sats(self, node):
        max_available_sats = 0
        edges = self.graph.out_edges(node)
        for edge in edges:
            max_available_sats = max(max_available_sats, self.graph.get_edge_data(edge[0], edge[1])[AVAILABLE_SATS])
        return max_available_sats

    def get_max_available_in_sats(self, node):
        max_available_sats = 0
        edges = self.graph.in_edges(node)
        for edge in edges:
            max_available_sats = max(max_available_sats, self.graph.get_edge_data(edge[0], edge[1])[AVAILABLE_SATS])
        return max_available_sats

    def query_channels(self, channels):
        # We count all the queries as one latency since they are all done in parallel
        query_delay = self.get_query_delay()
        self.simulate_delay(query_delay / 2)

        self.sc.record_rtt(self.query_rtts * math.ceil(
            len(channels) / 2))  # NOTE: We only need to query half of the nodes to get the balanced of all channels of the path
        self.sc.record_query(math.ceil(len(channels) / 2))
        response = []
        for channel in channels:
            src = channel[0]
            dst = channel[1]
            edge = self.graph.get_edge_data(src, dst)
            response.append(edge)

        self.simulate_delay(query_delay / 2)
        return response

    def get_query_delay(self):
        query_delay = self.query_delay * (
                1 + (self.rand.randint(-self.delay_randomness_threshold * 100,
                                       self.delay_randomness_threshold * 100) / 100)
        )
        return query_delay

    def get_hop_delay(self):
        hop_delay = self.hop_delay * (
                1 + (self.rand.randint(-self.delay_randomness_threshold * 100,
                                       self.delay_randomness_threshold * 100) / 100)
        )
        return hop_delay

    def execute_transaction(self, route, amount):
        self.sc.record_tx_try()
        for i in range(len(route) - 1):
            edge = self.graph.get_edge_data(route[i], route[i + 1])
            if edge[AVAILABLE_SATS] < amount:
                if self.config[REOPEN_ENABLED] and amount < edge[CAPACITY] / 2:
                    reverse_of_edge = self.graph.get_edge_data(route[i + 1], route[i])
                    while edge[LOCKED_SATS] > 0 or reverse_of_edge[LOCKED_SATS] > 0:
                        pass
                    edge[LOCK].acquire()
                    reverse_of_edge[LOCK].acquire()
                    edge[AVAILABLE_SATS] = edge[CAPACITY] / 2
                    reverse_of_edge[AVAILABLE_SATS] = edge[CAPACITY] / 2
                    edge[LOCKED_SATS] = 0
                    reverse_of_edge[LOCKED_SATS] = 0
                    edge[LOCK].release()
                    reverse_of_edge[LOCK].release()
                    self.sc.record_channel_reopen()
                    self.sc.record_rtt(self.tx_hop_rtts)  # NOTE: not accurate, have different delay and RTT for reopen
                    self.l.log("REOPENED CHANNEL, Transactions between reopens: " + str(
                        self.transactions_routed_from_last_reopen))
                    self.transactions_routed_from_last_reopen = 0
                else:
                    for j in range(0, i):
                        edge = self.graph.get_edge_data(route[j], route[j + 1])
                        edge[LOCK].acquire()
                        edge[AVAILABLE_SATS] += amount
                        edge[LOCKED_SATS] -= amount
                        edge[LOCK].release()
                        self.sc.record_rtt(self.tx_hop_rtts)
                        self.simulate_delay(self.get_hop_delay())
                    self.sc.record_tx_fail()
                    return False, (route[i], route[i + 1])
            edge[LOCK].acquire()
            edge[AVAILABLE_SATS] -= amount
            edge[LOCKED_SATS] += amount
            edge[LOCK].release()
            self.sc.record_rtt(self.tx_hop_rtts)
            self.simulate_delay(self.get_hop_delay())

        for i in range(len(route) - 1):
            edge = self.graph.get_edge_data(route[i], route[i + 1])
            reverse_edge = self.graph.get_edge_data(route[i + 1], route[i])
            edge[LOCK].acquire()
            reverse_edge[LOCK].acquire()
            edge[LOCKED_SATS] -= amount
            reverse_edge[AVAILABLE_SATS] += amount
            edge[LOCK].release()
            reverse_edge[LOCK].release()
            # NOTE: There should be some RTT count and delay here too, but it's not important for our results

        self.transactions_routed_from_last_reopen += 1
        self.sc.record_tx_success()
        return True, None

    def simulate_delay(self, delay):
        self.sc.record_network_latency(delay)
        time.sleep(delay)

    def build_graph_from_config(self):
        seed = self.config[SEED]
        n = self.config[NODES_NUM]
        m = self.config[CHANNELS_NUM]
        sats_min = self.config[SATS_MIN]
        sats_max = self.config[SATS_MAX]
        topology = self.config[TOPOLOGY]
        count_initial_channels_as_reopens = self.config[COUNT_INITIAL_CHANNELS_AS_REOPENS]

        if m < n - 1:
            raise ValueError(
                "The number of channels must be at least n-1 for the graph to be connected."
            )

        i = 0
        graph = self.build_undirected_graph_with_topology(topology, n, m, seed + i)
        while not nx.is_connected(graph) or nx.number_of_selfloops(graph) != 0:  # Possible infinite loop
            i += 1
            graph = self.build_undirected_graph_with_topology(topology, n, m, seed + i)

        if count_initial_channels_as_reopens:
            self.sc.record_channel_reopen(graph.number_of_edges())

        graph = self.build_directed_graph_with_channel_balances_from_undirected_graph(graph, sats_min, sats_max)

        return graph

    def build_directed_graph_with_channel_balances_from_undirected_graph(self, base_graph, sats_min, sats_max):
        edges = base_graph.edges()
        graph = nx.DiGraph()
        for edge in edges:
            edge_data = base_graph.get_edge_data(edge[0], edge[1])
            capacity = edge_data.get(CAPACITY, 0)
            right_sats = 0
            left_sats = 0
            if capacity and not self.config[OVERWRITE_BALANCES]:
                if self.config[CAPACITY_DISTRIBUTION] == DISTRIBUTION_HALF:
                    right_sats = math.ceil(capacity / 2)
                    left_sats = math.floor(capacity / 2)
                elif self.config[CAPACITY_DISTRIBUTION] == DISTRIBUTION_RANDOM:
                    r = self.rand.random()
                    right_sats = math.ceil(capacity * r)
                    left_sats = math.floor(capacity * (1 - r))
            else:
                right_sats = self.rand.randint(sats_min, sats_max)
                left_sats = self.rand.randint(sats_min, sats_max)

            saturaton = self.rand.random()
            if saturaton < self.config[SATURATION_PROBABILITY]:
                if saturaton < self.config[SATURATION_PROBABILITY] / 2:
                    right_sats = 0
                    left_sats += right_sats
                else:
                    left_sats = 0
                    right_sats += left_sats

            graph.add_edge(
                edge[0],
                edge[1],
                capacity=right_sats + left_sats,
                available_sats=right_sats,
                locked_sats=0,
                lock=Lock(),
            )
            graph.add_edge(
                edge[1],
                edge[0],
                capacity=right_sats + left_sats,
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
            return nx.star_graph(n - 1)  # n-1 because the center node is not counted
        elif topology == TOPOLOGY_COMPLETE:
            raise NotImplementedError
        elif topology == TOPOLOGY_FROM_FILE:
            file_path = self.config[TOPOLOGY_FILE]
            return self.load_graph_from_file(file_path)
        elif topology == TOPOLOGY_BALANCED_TREE:
            branching_factor = 2
            height = math.ceil(math.log2(n))
            graph = nx.balanced_tree(branching_factor, height)
            if 2 ** height - 1 > n:
                num_of_nodes_to_remove = 2 ** height - 1 - n
                leaf_nodes = [node for node in graph if nx.degree(graph, node) == 1]
                nodes_to_remove = leaf_nodes[-num_of_nodes_to_remove:]
                graph.remove_nodes_from(nodes_to_remove)
            return graph
        else:
            raise ValueError("Unknown topology: " + topology)

    def load_graph_from_file(self, file_path):
        f = open(file_path, 'r', encoding="utf8")
        json_data = json.load(f)
        f.close()

        graph = nx.Graph()

        for channel in json_data['channels']:
            graph.add_edge(
                channel['source'], channel['destination'], key=channel['short_channel_id'],
                capacity=channel['satoshis'])

        biggest_island_size = 0
        islands = []
        cc = nx.connected_components(graph)
        for i, c in enumerate(cc):
            biggest_island_size = max(biggest_island_size, len(c))
            islands.append(c)

        for island in islands:
            if len(island) < biggest_island_size:
                graph.remove_nodes_from(island)
                self.l.log(f"Removing island with nodes: {island}")
        return graph

    def dump(self):
        self.l.log("Dumping the network:")
        self.l.log("Nodes: " + str(self.graph.nodes()))
        self.l.log("Edges: " + str(self.graph.edges(data=True)))

    def dump_graph_metrics(self):
        edges = self.graph.edges(data=True)
        capacities = [edge[2][CAPACITY] for edge in edges]
        self.dump()
        self.l.metric(
            {
                "capacities_avg": sum(capacities) / len(capacities),
                "capacities_min": min(capacities),
                "capacities_max": max(capacities),
                "capacities_median": statistics.median(capacities),
                "num_of_channels": len(edges) / 2,  # NOTE: Each channel is represented twice in the directed graph
                "num_of_nodes": len(self.graph.nodes()),
            }
        )
