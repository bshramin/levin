import os
from datetime import datetime
from queue import Queue
from threading import Thread
from .consts import Status, ENABLED


class Logger:
    def __init__(self, name, config):
        self.log_enabled = config[ENABLED]
        self.stop_request = False
        self.name = name
        self.log_q = Queue(maxsize=10000)
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
            log = self.log_q.get()
            try:
                self.file.write(log + "\n")
                self.file.flush()
            except:
                pass  # Ignore logs with unknown format

        self.file.close()
        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()

    def log(self, message):
        if self.log_enabled:
            self.log_q.put(str(message))

    def metric(self, message):
        self.log_q.put(str(message))
