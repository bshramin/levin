import os
from datetime import datetime
from queue import Queue
from threading import Thread
from .consts import Status, ENABLED


class Logger:
    def __init__(self, name, config):
        if config[ENABLED] == False:
            self.stop_request = True
            self.enabled = False
            self.status = Status.STOPPED
            return
        self.stop_request = False
        self.enabled = True
        self.name = name
        self.log_q = Queue(maxsize=1000)
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
        while not self.stop_request:
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
        if self.enabled:
            self.log_q.put(message)
