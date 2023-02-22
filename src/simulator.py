from time import sleep
from queue import Queue
from threading import Thread
import toml


class Simulator:
    name = ""
    config = {}
    out_q = None
    in_q = None
    log_q = None
    status = "not initialized"  # TODO: use enums
    stop_request = False

    def __init__(self, name, log_q, config_path="configs"):
        self.name = name
        self.out_q = Queue()
        self.in_q = Queue()
        self.log_q = log_q
        self.status2 = "not started"
        self.read_config(config_path)

    def read_config(self, config_path):
        full_path = config_path + "/" + self.name + ".toml"
        self.log("Reading config: " + full_path)
        self.config = toml.load(full_path)

    def start(self):
        _ = Thread(target=self.run).start()
        _ = Thread(target=self.commands).start()

    def run(self):
        self.status = "running"
        self.log("Starting the simulation.")

        while not self.stop_request:
            sleep(1)
            self.log("Hello from " + self.name)

        self.status = "stopped"
        self.log("Stopping the simulation.")
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
