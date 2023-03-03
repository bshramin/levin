import toml
from time import sleep
from queue import Queue
from threading import Thread
from .consts import Status, LOGGING_CONFIG, AGENT_CONFIG, NUM_OF_AGENTS, NETWORK_CONFIG
from .network import Network
from .agent import Agent
from .logger import Logger
from .stats import StatCollector


class Simulator:
    def __init__(self, name):
        self.config = None
        self.network = None
        self.stop_request = False
        self.name = name
        self.read_config()
        self.l = Logger(name, self.config[LOGGING_CONFIG])
        self.simulation_stop_request_q = Queue()
        self.l.log(
            "Config read: \n"
            + str(self.config)
            + "\n********** end of config dump **********"
        )
        self.sc = StatCollector(name, self.l)
        self.sc.record_config(self.config)
        self.agents = []
        self.status = Status.WAITING

    def read_config(self):
        full_path = "configs/" + self.name + ".toml"
        self.config = toml.load(full_path)

    def generate_agents(self):
        config = self.config[AGENT_CONFIG]
        n = config[NUM_OF_AGENTS]

        self.l.log("Generating " + str(n) + " agents.")
        for i in range(n):
            self.agents.append(
                Agent(self.name, i, self.l, self.sc, self.network, config, self.simulation_stop_request_q)
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

    def stop_logger_and_stat_collector(self):
        self.l.stop_request = True
        self.sc.stop_request = True

        self.l.log("exit")
        self.sc.dummy()

        while self.l.status != Status.STOPPED or self.sc.status != Status.STOPPED:
            sleep(0.1)

    def run(self):
        self.status = Status.RUNNING
        self.l.log("Starting the simulation.")

        self.network = Network(self.name, self.l, self.sc, self.config[NETWORK_CONFIG])
        # self.network.dump()
        self.generate_agents()
        self.start_agents()

        while True:
            if self.stop_request:
                self.stop_agents()
                break
            if Status.RUNNING not in [agent.status for agent in self.agents]:
                break
            if not self.simulation_stop_request_q.empty():
                self.stop_request = True
                self.stop_agents()
                break
            sleep(1)

        self.stop_logger_and_stat_collector()
        self.l.log("Stopping the simulation.")
        print("Simulator " + self.name + " stopped.")
        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()
