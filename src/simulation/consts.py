from enum import Enum


class Status(Enum):
    NOT_INITIALIZED = 1
    WAITING = 2
    RUNNING = 3
    STOPPED = 4


class StatType(Enum):
    RTT_COUNT = "rtt_count"
    TX_SUCCESS_COUNT = "tx_success_count"
    TX_TRY_COUNT = "tx_try_count"
    TX_NO_ROUTE = "tx_no_route"


# Config keys

NETWORK_CONFIG = "network"
SEED = "seed"

AGENT_CONFIG = "agents"
NUM_OF_AGENTS = "num_of_agents"
TX_DELAY = "tx_delay"
TX_AMOUNT_MIN = "tx_amount_min"
TX_AMOUNT_MAX = "tx_amount_max"

ROUTING_CONFIG = "routing"
ROUTING_ALGORITHM = "routing_algorithm"


class RoutingAlgorithms(Enum):
    SHORTEST_PATH = "shortest_path"
    TRANSPARENT = "transparent"
