import toml
from time import sleep
from queue import Queue
from threading import Thread
from .consts import Status, NETWORK_CONFIG
from .network import Network
from .agent import Agent, generate_agents


class Simulator:
    name = ""
    config = {}
    out_q = None
    in_q = None
    log_q = None
    status = Status.NOT_INITIALIZED
    stop_request = False
    network = None
    agents = []

    def __init__(self, name, log_q, config_path="configs"):
        self.name = name
        self.out_q = Queue(maxsize=1)  # Non-blocking for 1 message
        self.in_q = Queue(maxsize=1)
        self.log_q = log_q
        self.status = Status.WAITING
        self.read_config(config_path)

    def read_config(self, config_path):
        full_path = config_path + "/" + self.name + ".toml"
        self.log("Reading config: " + full_path)
        self.config = toml.load(full_path)
        self.log(
            "Config read: \n"
            + str(self.config)
            + "\n********** end of config dump **********"
        )

    def start(self):
        _ = Thread(target=self.run).start()
        _ = Thread(target=self.commands).start()

    def run(self):
        self.status = Status.RUNNING
        self.log("Starting the simulation.")

        self.network = Network(self.name, self.log_q, self.config["network"])
        self.network.dump()
        self.agents = generate_agents(
            self.name, self.log_q, self.network, self.config["agents"]
        )
        
        # TODO: Implement the simulation logic here.

        self.log("Stopping the simulation.")
        self.status = Status.STOPPED
        print("Simulator " + self.name + " stopped.")
        self.out_q.put("stopped")

    def log(self, msg):
        self.log_q.put({"task": self.name, "message": msg})

    def commands(self):
        while True:
            command = str(self.in_q.get())
            if command == "stop":
                self.stop_request = True
                return
            if command == "status":
                self.out_q.put(self.status)
