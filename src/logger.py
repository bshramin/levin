from datetime import datetime
from queue import Queue
from threading import Thread


class Logger:
    log_directory = None
    log_q = None
    in_q = None
    out_q = None
    log_files = {}
    stop_request = False

    def __init__(
        self,
        log_q,
        names,
        log_directory="logs",
    ):
        self.in_q = Queue()
        self.out_q = Queue()
        self.log_directory = log_directory
        self.log_q = log_q
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.open_log_files(log_directory, names, timestamp)

    def open_log_files(self, log_directory, names, timestamp):
        for name in names:
            f = open(log_directory + "/" + name + "-" + timestamp + ".log", "w+")
            self.log_files[name] = f

    def run(self):
        while not self.stop_request:
            try:
                log = self.log_q.get(timeout=1)
                self.log_files[log["task"]].write(log["message"] + "\n")
                self.log_files[log["task"]].flush()
            except:
                pass

        for log_file in self.log_files:
            self.log_files[log_file].close()

        self.out_q.put("stopped")

    def commands(self):
        while True:
            command = str(self.in_q.get())
            if command == "stop":
                self.stop_request = True
                return

    def start(self):
        _ = Thread(target=self.run).start()
        _ = Thread(target=self.commands).start()
