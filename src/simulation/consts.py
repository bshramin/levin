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
    SIMULATION_DURATION = "simulation_duration"


# Config keys

# Logging
LOGGING_CONFIG = "logging"
ENABLED = "enabled"

# Network
NETWORK_CONFIG = "network"
SEED = "seed"

# Agents
AGENT_CONFIG = "agents"
NUM_OF_TRANSACTIONS = "num_of_transactions"
NUM_OF_AGENTS = "num_of_agents"
TX_REST = "tx_rest"
TX_AMOUNT_MIN = "tx_amount_min"
TX_AMOUNT_MAX = "tx_amount_max"
ROUTING_ALGORITHM = "routing_algorithm"


class RoutingAlgorithms(Enum):
    SHORTEST_PATH = "shortest_path"
    TRANSPARENT = "transparent"
