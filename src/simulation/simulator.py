from copy import deepcopy

import toml
from time import sleep
from threading import Thread
from .consts import Status, LOGGING_CONFIG, AGENT_CONFIG, NUM_OF_AGENTS, NETWORK_CONFIG, SIMULATION_CONFIG, \
    NUM_OF_ROUNDS, SEED
from .network import Network
from .agent import Agent
from .logger import Logger
from .stats import StatCollector


class Simulator:
    def __init__(self, name):
        self.config = None
        self.stop_request = False
        self.name = name
        self.num_of_rounds = None
        self.num_of_agents = None
        self.read_config()
        self.l = Logger(name, self.config[LOGGING_CONFIG])  # TODO: currently no way to distinguish rounds from each other
        self.l.log(
            "Config read: \n"
            + str(self.config)
            + "\n********** end of config dump **********"
        )
        self.sc = StatCollector(name, self.l, self.num_of_rounds)
        self.sc.record_config(self.config)
        self.agents = []
        self.status = Status.WAITING

    def read_config(self):
        full_path = "configs/" + self.name + ".toml"
        self.config = toml.load(full_path)
        self.num_of_rounds = self.config[SIMULATION_CONFIG][NUM_OF_ROUNDS]
        self.num_of_agents = self.config[SIMULATION_CONFIG][NUM_OF_AGENTS]

    def generate_agents(self, network, agents_config):
        self.l.log("Generating " + str(self.num_of_agents) + " agents.")
        for i in range(self.num_of_agents):
            self.agents.append(
                Agent(self.name, i, self.l, self.sc, network, agents_config)
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
        self.l.log("Setting up the simulation.")

        num_of_rounds = self.num_of_rounds
        network_config = deepcopy(self.config[NETWORK_CONFIG])
        agents_config = deepcopy(self.config[AGENT_CONFIG])
        for i in range(num_of_rounds):
            network_config[SEED] = hash(str(network_config[SEED]))
            agents_config[SEED] = hash(str(agents_config[SEED]))
            network = Network(self.name, self.l, self.sc, network_config)
            self.generate_agents(network, agents_config)
            self.l.log(f"Round {i} generated.")

        self.l.log("Starting the simulation.")
        self.start_agents()

        while not self.stop_request:
            if Status.RUNNING not in [agent.status for agent in self.agents]:
                break
            sleep(0.1)

        self.stop_request = True
        self.stop_agents()
        self.l.log("Stopping the simulation.")
        self.stop_logger_and_stat_collector()
        print("Simulator " + self.name + " stopped.")
        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()
