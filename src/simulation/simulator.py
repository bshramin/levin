import toml
from time import sleep
from threading import Thread
from .consts import Status
from .network import Network
from .agent import Agent
from .logger import Logger
from .stats import StatCollector


class Simulator:
    name = ""
    l = None  # Logger
    sc = None  # StatCollector
    config = {}
    status = Status.NOT_INITIALIZED
    stop_request = False
    network = None
    agents = []

    def __init__(self, name):
        self.name = name
        self.l = Logger(name)
        self.sc = StatCollector(name)
        self.read_config()
        self.status = Status.WAITING

    def read_config(self):
        full_path = "configs/" + self.name + ".toml"
        self.l.log("Reading config: " + full_path)
        self.config = toml.load(full_path)
        self.l.log(
            "Config read: \n"
            + str(self.config)
            + "\n********** end of config dump **********"
        )

    def generate_agents(self):
        config = self.config["agents"]
        n = config["num_of_agents"]

        self.l.log("Generating " + str(n) + " agents.")
        for i in range(n):
            self.agents.append(Agent(self.name, i, self.l, self.network, config))

    def start_agents(self):
        for agent in self.agents:
            agent.start()

    def stop_agents(self):
        for agent in self.agents:
            agent.stop_request = True

        for agent in self.agents:
            while agent.status != Status.STOPPED:
                sleep(0.1)

    def stop_logger_and_stat_collector(self):
        self.l.stop_request = True
        self.sc.stop_request = True

        self.l.log_q.put("exit")
        self.sc.stat_q.put("exit")

        while self.l.status != Status.STOPPED or self.sc.status != Status.STOPPED:
            sleep(0.1)

    def run(self):
        self.status = Status.RUNNING
        self.l.log("Starting the simulation.")

        self.network = Network(self.name, self.l, self.sc, self.config["network"])
        self.network.dump()
        self.generate_agents()
        self.start_agents()

        while not self.stop_request:
            sleep(0.5)

        self.stop_agents()
        self.stop_logger_and_stat_collector()
        self.l.log("Stopping the simulation.")
        print("Simulator " + self.name + " stopped.")
        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()
