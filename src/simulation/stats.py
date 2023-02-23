import os
from datetime import datetime
from queue import Queue
from threading import Thread
from simulation.consts import Status, StatType


class StatCollector:
    name = ""
    stat_q = None
    stop_request = False
    status = Status.NOT_INITIALIZED
    stat_data = {}

    def __init__(
        self,
        name,
    ):
        self.name = name
        self.stat_q = Queue(maxsize=10000)
        self.initialize_data()
        self.status = Status.WAITING
        self.start()

    def run(self):
        self.status = Status.RUNNING
        while not self.stop_request:
            stat = self.stat_q.get()
            try:
                type = stat["type"]
                value = stat["value"]

                if type in [
                    StatType.RTT_COUNT,
                    StatType.TX_SUCCESS_COUNT,
                    StatType.TX_TRY_COUNT,
                    StatType.TX_FAIL_COUNT,
                ]:
                    self.stat_data[type.value] += value

            except:
                pass  # Ignore stats with unknown format

        self.write_stats_to_file()
        self.status = Status.STOPPED

    def write_stats_to_file(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = "stats/" + self.name + "/" + timestamp + ".stat"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w+")
        f.write(str(self.stat_data))
        f.close()

    def initialize_data(self):
        self.stat_data[StatType.RTT_COUNT.value] = 0
        self.stat_data[StatType.TX_SUCCESS_COUNT.value] = 0
        self.stat_data[StatType.TX_TRY_COUNT.value] = 0
        self.stat_data[StatType.TX_FAIL_COUNT.value] = 0

    def start(self):
        thread = Thread(target=self.run)
        thread.start()

    # Helpers
    def record_rtt(self, count):
        self.stat_q.put({"value": count, "type": StatType.RTT_COUNT})

    def record_tx_try(self, count):
        self.stat_q.put({"value": count, "type": StatType.TX_TRY_COUNT})

    def record_tx_success(self, count):
        self.stat_q.put({"value": count, "type": StatType.TX_SUCCESS_COUNT})

    def record_tx_fail(self, count):
        self.stat_q.put({"value": count, "type": StatType.TX_FAIL_COUNT})
