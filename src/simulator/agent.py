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
from .routers import ShortestPathRouter


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
        self.rand = Random(config[SEED] + id)
        self.status = Status.WAITING
        self.set_router(config)

    def set_router(self, config):
        if config[ROUTING_ALGORITHM] == RoutingAlgorithms.SHORTEST_PATH.value:
            self.router = ShortestPathRouter()

    def send_transaction(self):
        src, dst = self.choose_src_and_dst()
        amount = self.choose_amount()
        self.log(
            f"sending transaction from {str(src)} to {str(dst)} amount: {str(amount)}"
        )
        try:
            network_graph_copy = self.network.graph.copy()
            route = self.router.find_route(network_graph_copy, src, dst)
            is_success = False

            while not is_success:
                is_success, error_edge = self.network.execute_transaction(route, amount)
                if is_success:
                    self.log("transaction succeeded")
                    break

                network_graph_copy.remove_edge(error_edge[0], error_edge[1])
                route = self.router.find_route(network_graph_copy, src, dst)
        except Exception as e:
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
        while True:
            sleep(self.config[TX_DELAY])
            self.send_transaction()
            if self.stop_request:
                self.log("stopped")
                self.status = Status.STOPPED
                break

    def start(self):
        thread = Thread(target=self.run)
        thread.start()

    def log(self, msg):
        self.log_q.put({"task": self.task_name, "message": f"Agent {self.id}: {msg}"})
