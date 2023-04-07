import os
from datetime import datetime
from multiprocessing import Process, Manager
from queue import Empty
from time import sleep

from .consts import Status, ENABLED


class Logger:
    def __init__(self, name, config, control_queue):
        self.manager = Manager()
        self.control_queue = control_queue
        self.log_enabled = config[ENABLED]
        self.stop_request = False
        self.name = name
        self.log_q = self.manager.Queue(maxsize=100000000)
        self.open_log_file(name)
        self.status = Status.WAITING
        self.start()

    def open_log_file(self, name):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = "logs/" + name + "/" + timestamp + ".log"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w+")
        self.file = f

    def run(self):
        self.status = Status.RUNNING
        while not self.stop_request or not self.log_q.empty():
            try:
                if not self.stop_request:
                    line = self.control_queue.get_nowait()
                    if line == "exit":
                        self.stop_request = True
            except Empty:
                pass

            try:
                log = self.log_q.get_nowait()
                self.file.write(log + "\n")
                self.file.flush()
            except Empty:
                continue

        self.file.close()
        self.control_queue.put("done")
        self.status = Status.STOPPED

    def start(self):
        thread = Process(target=self.run)
        thread.start()

    def log(self, message):
        if self.log_enabled:
            self.log_q.put(str(message))

    def metric(self, message):
        self.log_q.put(str(message))
