import os
from datetime import datetime
from queue import Queue
from threading import Thread
from .consts import Status


class Logger:
    log_directory = None
    log_q = None
    log_files = {}
    stop_request = False
    status = Status.NOT_INITIALIZED

    def __init__(
        self,
        log_q,
        names,
        log_directory="logs",
    ):
        self.log_directory = log_directory
        self.log_q = log_q
        self.open_log_files(log_directory, names)
        self.status = Status.WAITING

    def open_log_files(self, log_directory, names):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        for name in names:
            file_name = log_directory + "/" + name + "/" + timestamp + ".log"
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            f = open(file_name, "w+")
            self.log_files[name] = f

    def run(self):
        self.status = Status.RUNNING
        while not self.stop_request:
            log = self.log_q.get()
            try:
                file = self.log_files[log["task"]]
                file.write(log["message"] + "\n")
                file.flush()
            except:
                pass  # Ignore logs with unknown format

        for log_file in self.log_files:
            self.log_files[log_file].close()

        self.status = Status.STOPPED

    def start(self):
        thread = Thread(target=self.run)
        thread.start()
