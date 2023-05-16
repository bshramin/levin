import hashlib
from multiprocessing import Process
from random import Random
from time import sleep

from .consts import (
    Status,
    TX_REST,
    SEED,
    TX_AMOUNT_MAX,
    TX_AMOUNT_MIN,
    ROUTING_ALGORITHM,
    NUM_OF_TRANSACTIONS,
    TX_MAX_ROUTE_TRIES,
    RoutingAlgorithms, CHECK_SOURCE_BALANCE, TX_MAX_QUERY_PER_TX_TRY, SRC_DST, RANDOM, FIXED_PAIRS, BIG_TO_SMALL,
)
from .routers import ShortestPathRouter, TransparentRouter


class Agent:
    def __init__(self, task_name, id, logger, stats_collector, network, config, control_queue):
        self.control_queue = control_queue
        self.stop_request = False
        self.task_name = task_name
        self.id = id
        self.l = logger
        self.sc = stats_collector
        self.config = config
        self.network = network
        self.router = None
        self.rand = Random(config[SEED] + id)
        self.stop_request = False
        self.status = Status.WAITING
        self.total_transactions = 0
        self.set_router()

    def set_router(self):
        routing_algorithm = self.config[ROUTING_ALGORITHM]
        if routing_algorithm == RoutingAlgorithms.SHORTEST_PATH.value:
            self.router = ShortestPathRouter()
        elif routing_algorithm == RoutingAlgorithms.TRANSPARENT.value:
            self.router = TransparentRouter(self.config[TX_MAX_QUERY_PER_TX_TRY])
        else:
            raise Exception("invalid routing algorithm: " + config[ROUTING_ALGORITHM])

    def send_transaction(self):
        src, dst = self.choose_src_and_dst()
        amount = self.choose_amount()
        while (self.config[CHECK_SOURCE_BALANCE] and (
                self.network.get_max_available_out_sats(src) < amount or
                self.network.get_max_available_in_sats(dst) < amount
        )):
            self.log(f"sending {amount} sats from {src}, not enough balance, choosing new src and dst")
            src, dst = self.choose_src_and_dst()
            amount = self.choose_amount()
        self.log(f"sending transaction from {str(src)} to {str(dst)} amount: {str(amount)}")
        is_success = False
        error_edges = []
        routes_tried = 0
        first_route = None
        reopen_request = False
        while not is_success and routes_tried <= self.config[TX_MAX_ROUTE_TRIES]:
            route, error_edges = self.router.find_route(
                self.network, src, dst, amount, error_edges
            )
            if len(route) == 0 and routes_tried == 0:
                break
            routes_tried += 1
            if routes_tried == self.config[TX_MAX_ROUTE_TRIES] or len(route) == 0:
                reopen_request = True
                if routes_tried > 1:
                    route = first_route
            is_success, error_edge = self.network.execute_transaction(route, amount, reopen_request)
            if is_success:
                self.log("transaction succeeded")
                return
            error_edges.append(error_edge)
            if routes_tried == 1:
                first_route = route
        self.tx_routing_failed()

    def tx_routing_failed(self):
        self.sc.record_tx_no_route()
        self.log("transaction failed - no route")

    def choose_src_and_dst(self):
        nodes = list(self.network.graph.nodes())
        src = self.rand.choice(nodes)
        nodes.remove(src)
        dst = self.rand.choice(nodes)
        sr_dst = self.config[SRC_DST]
        if sr_dst == RANDOM:
            pass
        elif sr_dst == FIXED_PAIRS:
            if src < dst:
                src, dst = dst, src
            combination = str(src) + str(dst)
            combination_hash = int(hashlib.sha256(combination.encode('utf-8')).hexdigest(), base=16)
            if combination_hash % 2 == 0:
                src, dst = dst, src
        elif sr_dst == BIG_TO_SMALL:
            src_hash = int(hashlib.sha256(str(src).encode('utf-8')).hexdigest(), base=16)
            dst_hash = int(hashlib.sha256(str(dst).encode('utf-8')).hexdigest(), base=16)
            if src_hash < dst_hash:
                src, dst = dst, src
        else:
            raise Exception("invalid src dst config: " + str(sr_dst))
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
        self.control_queue.put("done")

    def start(self):
        thread = Process(target=self.run)
        thread.start()

    def log(self, msg):
        self.l.log(f"Agent {self.id}: ${msg}")
