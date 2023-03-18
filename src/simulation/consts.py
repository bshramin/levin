from enum import Enum


class Status(Enum):
    WAITING = 1
    RUNNING = 2
    STOPPED = 3


class StatType(Enum):
    DUMMY = "dummy"
    CONFIG = "config"
    RTT_COUNT = "rtt_count"
    TX_SUCCESS_COUNT = "tx_success_count"
    TX_TRY_COUNT = "tx_try_count"
    TX_NO_ROUTE = "tx_no_route"
    QUERY_COUNT = "query_count"
    SIMULATION_DURATION = "simulation_duration"
    TX_FAIL_COUNT = "tx_fail_count"
    CHANNELS_REOPEN_COUNT = "channels_reopen_count"


# Config keys

# Simulation
SIMULATION_CONFIG = "simulation"
NUM_OF_ROUNDS = "num_of_rounds"
NUM_OF_AGENTS = "num_of_agents"

# Logging
LOGGING_CONFIG = "logging"
ENABLED = "enabled"

# Network
NETWORK_CONFIG = "network"
SEED = "seed"
TOPOLOGY = "topology"
TOPOLOGY_RANDOM = "random"
TOPOLOGY_PATH = "path"
TOPOLOGY_STAR = "star"
TOPOLOGY_COMPLETE = "complete"
TOPOLOGY_BALANCED_TREE = "balanced_tree"
TOPOLOGY_FILE = "file"
TOPOLOGY_FILE_PATH = "path"
NODES_NUM = "nodes_num"
CHANNELS_NUM = "channels_num"
SATS_MIN = "sats_min"
SATS_MAX = "sats_max"
REOPEN_ENABLED = "reopen_enabled"
COUNT_INITIAL_CHANNELS_AS_REOPENS = "count_initial_channels_as_reopens"
DELAY_ENABLED = "delay_enabled"
RTT_DELAY = "rtt_delay"
QUERY_RTTS = "query_rtts"
TX_HOP_RTTS = "tx_hop_rtts"


# Agents
AGENT_CONFIG = "agents"
CHECK_SOURCE_BALANCE = "check_source_balance"
NUM_OF_TRANSACTIONS = "num_of_transactions"
TX_REST = "tx_rest"
TX_AMOUNT_MIN = "tx_amount_min"
TX_AMOUNT_MAX = "tx_amount_max"
ROUTING_ALGORITHM = "routing_algorithm"
TX_MAX_ROUTE_TRIES = "tx_max_route_tries"


class RoutingAlgorithms(Enum):
    SHORTEST_PATH = "shortest_path"
    TRANSPARENT = "transparent"
