from threading import Thread
from time import sleep
from .consts import (
    Status,
    TX_REST,
    SEED,
    TX_AMOUNT_MAX,
    TX_AMOUNT_MIN,
    ROUTING_ALGORITHM,
    NUM_OF_TRANSACTIONS,
    RoutingAlgorithms,
)
from random import Random
from .routers import ShortestPathRouter, TransparentRouter


class Agent:
    def __init__(self, task_name, id, logger, stats_collector, network, config):
        self.stop_request = False
        self.task_name = task_name
        self.id = id
        self.l = logger
        self.sc = stats_collector
        self.config = config
        self.network = network
        self.rand = Random(config[SEED] + id)
        self.stop_request = False
        self.status = Status.WAITING
        self.total_transactions = 0
        self.set_router(config)

    def set_router(self, config):
        if config[ROUTING_ALGORITHM] == RoutingAlgorithms.SHORTEST_PATH.value:
            self.router = ShortestPathRouter()
        elif config[ROUTING_ALGORITHM] == RoutingAlgorithms.TRANSPARENT.value:
            self.router = TransparentRouter()

    def send_transaction(self):
        src, dst = self.choose_src_and_dst()
        amount = self.choose_amount()
        self.log(
            f"sending transaction from {str(src)} to {str(dst)} amount: {str(amount)}"
        )
        try:
            is_success = False
            error_edges = []
            while not is_success:
                route = self.router.find_route(
                    self.network, src, dst, amount, error_edges
                )
                if len(route) == 0:
                    self.log("transaction failed - no route")
                    self.sc.record_tx_no_route()
                    break
                self.sc.record_tx_try()
                is_success, error_edge = self.network.execute_transaction(route, amount)
                if is_success:
                    self.sc.record_tx_success()
                    self.log("transaction succeeded")
                    break
                error_edges.append(error_edge)
        except Exception as e:
            self.sc.record_tx_no_route()
            self.log(f"transaction failed {e}")

    def choose_src_and_dst(self):
        nodes = list(self.network.graph.nodes())
        src = self.rand.choice(nodes)
        nodes.remove(src)
        dst = self.rand.choice(nodes)
        return src, dst

    def choose_amount(self):
        return self.rand.randint(self.config[TX_AMOUNT_MIN], self.config[TX_AMOUNT_MAX])

    def run(self):
        self.log("started")
        self.status = Status.RUNNING
        while self.total_transactions < self.config[NUM_OF_TRANSACTIONS]:
            sleep(self.config[TX_REST])
            self.send_transaction()
            self.total_transactions += 1
            if self.stop_request:
                break
        self.log("stopped")
        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()

    def log(self, msg):
        self.l.log(f"Agent {self.id}: ${msg}")
