import toml
from time import sleep
from queue import Queue
from threading import Thread
from .consts import Status, NETWORK_CONFIG
from .network import Network
from .agent import Agent


class Simulator:
    name = ""
    config = {}
    log_q = None
    status = Status.NOT_INITIALIZED
    stop_request = False
    network = None
    agents = []

    def __init__(self, name, log_q, config_path="configs"):
        self.name = name
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

    def generate_agents(self):
        config = self.config["agents"]
        n = config["num_of_agents"]

        self.log("Generating " + str(n) + " agents.")
        for i in range(n):
            self.agents.append(
                Agent(self.name, str(i), self.log_q, self.network, config)
            )

    def start_agents(self):
        for agent in self.agents:
            agent.start()

    def stop_agents(self):
        for agent in self.agents:
            agent.stop_request = True

        for agent in self.agents:
            while agent.status != Status.STOPPED:
                sleep(0.1)

    def run(self):
        self.status = Status.RUNNING
        self.log("Starting the simulation.")

        self.network = Network(self.name, self.log_q, self.config["network"])
        self.network.dump()
        self.generate_agents()
        self.start_agents()

        while not self.stop_request:
            sleep(0.5)

        self.stop_agents()
        self.log("Stopping the simulation.")
        print("Simulator " + self.name + " stopped.")
        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()

    def log(self, msg):
        self.log_q.put({"task": self.name, "message": msg})
