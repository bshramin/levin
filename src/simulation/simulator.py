import hashlib
from copy import deepcopy
from queue import Empty

import toml
from time import sleep
from multiprocessing import Process, Manager
from .consts import Status, LOGGING_CONFIG, AGENT_CONFIG, NUM_OF_AGENTS, NETWORK_CONFIG, SIMULATION_CONFIG, \
    NUM_OF_ROUNDS, SEED, PRINT_INTERVAL
from .network import Network
from .agent import Agent
from .logger import Logger
from .stats import StatCollector


class Simulator:
    def __init__(self, name, control_queue):
        self.manager = Manager()
        self.control_queue = control_queue
        self.log_control_queue = self.manager.Queue()
        self.stats_control_queue = self.manager.Queue()
        self.config = None
        self.stop_request = False
        self.name = name
        self.num_of_rounds = None
        self.num_of_agents = None
        self.read_config()
        self.l = Logger(name, self.config[LOGGING_CONFIG], self.log_control_queue)
        self.l.log(
            "Config read: \n"
            + str(self.config)
            + "\n********** end of config dump **********"
        )
        print_interval = self.config[LOGGING_CONFIG][PRINT_INTERVAL]
        self.sc = StatCollector(name, self.l, self.num_of_rounds, print_interval, self.stats_control_queue)
        self.sc.record_config(self.config)
        self.agents = []
        self.networks = []
        self.status = Status.WAITING
        self.agent_queue = self.manager.Queue()

    def read_config(self):
        full_path = "configs/" + self.name + ".toml"
        self.config = toml.load(full_path)
        self.num_of_rounds = self.config[SIMULATION_CONFIG][NUM_OF_ROUNDS]
        self.num_of_agents = self.config[SIMULATION_CONFIG][NUM_OF_AGENTS]

    def generate_agents(self, network, agents_config):
        self.l.log("Generating " + str(self.num_of_agents) + " agents.")
        for i in range(self.num_of_agents):
            self.agents.append(
                Agent(self.name, i, self.l, self.sc, network, agents_config, self.agent_queue)
            )

    def start_agents(self):
        for agent in self.agents:
            agent.start()

    def stop_logger_and_stat_collector(self):
        self.log_control_queue.put("exit")
        sleep(1)
        self.log_control_queue.get()

        self.stats_control_queue.put("exit")
        sleep(1)
        self.stats_control_queue.get()

    def run(self):
        self.status = Status.RUNNING
        self.l.log("Setting up the simulation.")

        num_of_rounds = self.num_of_rounds
        network_config = deepcopy(self.config[NETWORK_CONFIG])
        agents_config = deepcopy(self.config[AGENT_CONFIG])
        for i in range(num_of_rounds):
            network_config[SEED] = (2**32 - 1) & int(hashlib.sha256(bytes(network_config[SEED])).hexdigest(), base=16)
            agents_config[SEED] = (2**32 - 1) & int(hashlib.sha256(bytes(agents_config[SEED])).hexdigest(), base=16)
            self.networks.append(Network(self.name, self.l, self.sc, network_config))
            # self.networks[i].dump()
            self.generate_agents(self.networks[i], agents_config)
            self.l.log(f"Round {i} generated.")

        self.l.log("Starting the simulation.")
        self.start_agents()
        done_agents_num = 0
        while not self.stop_request:
            try:
                line = self.agent_queue.get_nowait()
                if line == "done":
                    done_agents_num += 1
            except Empty:
                pass
            if done_agents_num == len(self.agents):
                self.stop_request = True
            sleep(1)

        self.stop_request = True
        self.l.log("Stopping the simulation.")
        self.stop_logger_and_stat_collector()
        self.control_queue.put("done")
        print("Simulator " + self.name + " stopped.")
        self.status = Status.STOPPED

    def start(self):
        p = Process(target=self.run)
        p.start()
