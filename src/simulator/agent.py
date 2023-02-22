from threading import Thread
from time import sleep
from .consts import (
    Status,
    TX_DELAY,
    SEED,
    TX_AMOUNT_MAX,
    TX_AMOUNT_MIN,
    ROUTING_ALGORITHM,
    RoutingAlgorithms,
)
from random import Random
from routers import BFSRouter


class Agent:
    task_name = ""
    id = ""
    log_q = None
    config = {}
    network = None
    stop_request = False
    status = Status.NOT_INITIALIZED
    rand = None
    router = None

    def __init__(self, task_name, id, log_q, network, config):
        self.task_name = task_name
        self.id = id
        self.log_q = log_q
        self.config = config
        self.network = network
        self.rand = Random(config[SEED])
        self.status = Status.WAITING
        self.set_router(config)

    def set_router(self, config):
        if config[ROUTING_ALGORITHM] == RoutingAlgorithms.BFS:
            self.router = BFSRouter()

    def execute_transaction(self):
        # TODO: implement an actual transaction execution logic
        edges = self.network.graph.edges()
        edge = self.rand.choice(edges)
        amount = self.rand.randint(
            self.config[TX_AMOUNT_MIN], self.config[TX_AMOUNT_MAX]
        )
        # TODO: Edit the weight of both edges
        self.log("executing transaction")

    def run(self):
        self.log("started")
        self.status = Status.RUNNING
        while True:
            sleep(self.config[TX_DELAY])
            self.execute_transaction()
            if self.stop_request:
                self.log("stopped")
                self.status = Status.STOPPED
                break

    def start(self):
        thread = Thread(target=self.run)
        thread.start()

    def log(self, msg):
        self.log_q.put(
            {"task": self.task_name, "message": "Agent " + self.id + ": " + msg}
        )
