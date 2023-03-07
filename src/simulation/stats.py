import os
from datetime import datetime
from queue import Queue
from threading import Thread
from simulation.consts import Status, StatType


class StatCollector:
    def __init__(self, name, logger):
        self.stop_request = False
        self.name = name
        self.l = logger
        self.stat_q = Queue(maxsize=10000)
        self.initialize_data()
        self.status = Status.WAITING
        self.start()

    def run(self):
        #  There is only one instance running per simulation config so no need for locks
        self.status = Status.RUNNING
        while not self.stop_request or not self.stat_q.empty():
            stat = self.stat_q.get()
            try:
                type = stat["type"]
                value = stat.get("value", None)

                if type in [
                    StatType.RTT_COUNT,
                    StatType.TX_SUCCESS_COUNT,
                    StatType.TX_TRY_COUNT,
                    StatType.TX_NO_ROUTE,
                    StatType.QUERY_COUNT,
                ]:
                    self.stat_data[type.value] += value
                elif type == StatType.CONFIG:
                    self.stat_data[type.value] = value
                elif type == StatType.DUMMY:
                    pass
            except Exception as e:
                self.l.log(f"Unknown stat format: {str(stat)}, {str(e)}")

        self.stat_data[StatType.SIMULATION_DURATION.value] = str(datetime.now() - self.start_time)
        self.write_stats_to_file()
        self.status = Status.STOPPED

    def write_stats_to_file(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = "stats/" + self.name + "/" + timestamp + ".json"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w+")
        f.write(str(self.stat_data))
        f.close()

    def initialize_data(self):
        self.stat_data = {}
        self.stat_data[StatType.CONFIG.value] = None
        self.stat_data[StatType.RTT_COUNT.value] = 0
        self.stat_data[StatType.TX_SUCCESS_COUNT.value] = 0
        self.stat_data[StatType.TX_TRY_COUNT.value] = 0
        self.stat_data[StatType.TX_NO_ROUTE.value] = 0
        self.stat_data[StatType.QUERY_COUNT.value] = 0

    def start(self):
        self.start_time = datetime.now()
        thread = Thread(target=self.run)
        thread.start()

    # Helpers
    def dummy(self):
        self.stat_q.put({"type": StatType.DUMMY})

    def record_config(self, config):
        self.stat_q.put({"value": f"{config}", "type": StatType.CONFIG})

    def record_rtt(self, count):
        self.stat_q.put({"value": count, "type": StatType.RTT_COUNT})

    def record_query(self, count):
        self.stat_q.put({"value": count, "type": StatType.QUERY_COUNT})

    def record_tx_try(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_TRY_COUNT})

    def record_tx_success(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_SUCCESS_COUNT})

    def record_tx_no_route(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_NO_ROUTE})
