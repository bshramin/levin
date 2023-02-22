from threading import Thread
from time import sleep
from .consts import Status


class Agent:
    task_name = ""
    id = ""
    log_q = None
    config = {}
    network = None
    stop_request = False
    status = Status.NOT_INITIALIZED

    def __init__(self, task_name, id, log_q, network, config):
        self.task_name = task_name
        self.id = id
        self.log_q = log_q
        self.config = config
        self.network = network
        self.status = Status.WAITING

    def run(self):
        self.log("started")
        self.status = Status.RUNNING
        while True:
            sleep(0.5)  # Simulate some work
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
