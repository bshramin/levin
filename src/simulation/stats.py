import os
from datetime import datetime
from multiprocessing import Process, Manager
from queue import Empty

from simulation.consts import Status, StatType


class StatCollector:
    def __init__(self, name, logger, num_of_rounds, control_queue):
        self.control_queue = control_queue
        self.stop_request = False
        self.name = name
        self.l = logger
        self.num_of_rounds = num_of_rounds
        self.manager = Manager()
        self.stat_q = self.manager.Queue(maxsize=100000000)
        self.stat_data = None
        self.initialize_data()
        self.status = Status.WAITING
        self.start_time = None
        self.start()

    def run(self):
        #  There is only one instance running per simulation config so no need for locks
        self.status = Status.RUNNING
        while not self.stop_request or not self.stat_q.empty():
            try:
                if not self.stop_request:
                    line = self.control_queue.get_nowait()
                    if line == "exit":
                        self.stop_request = True
            except Empty:
                pass

            try:
                stat = self.stat_q.get_nowait()
                stat_type = stat["type"]
                value = stat.get("value", None)

                if stat_type in [
                    StatType.RTT_COUNT,
                    StatType.TX_SUCCESS_COUNT,
                    StatType.TX_TRY_COUNT,
                    StatType.TX_NO_ROUTE,
                    StatType.QUERY_COUNT,
                    StatType.TX_FAIL_COUNT,
                    StatType.CHANNELS_REOPEN_COUNT,
                    StatType.NETWORK_LATENCY,
                ]:
                    self.stat_data[stat_type.value] += value
                elif stat_type == StatType.CONFIG:
                    self.stat_data[stat_type.value] = value
                elif stat_type == StatType.DUMMY:
                    pass
            except:
                continue

        self.stat_data[StatType.SIMULATION_DURATION.value] = str(datetime.now() - self.start_time)
        self.write_stats_to_file()
        self.control_queue.put("done")
        self.status = Status.STOPPED

    def write_stats_to_file(self):
        for key in self.stat_data:
            if key not in [StatType.CONFIG.value, StatType.SIMULATION_DURATION.value]:
                self.stat_data[key] /= self.num_of_rounds

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = "stats/" + self.name + "/" + timestamp + ".json"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w+")
        f.write(str(self.stat_data))
        f.close()

    def initialize_data(self):
        self.stat_data = {
            StatType.CONFIG.value: None,
            StatType.RTT_COUNT.value: 0,
            StatType.TX_SUCCESS_COUNT.value: 0,
            StatType.TX_TRY_COUNT.value: 0,
            StatType.TX_NO_ROUTE.value: 0,
            StatType.QUERY_COUNT.value: 0,
            StatType.TX_FAIL_COUNT.value: 0,
            StatType.CHANNELS_REOPEN_COUNT.value: 0,
            StatType.NETWORK_LATENCY.value: 0,
        }

    def start(self):
        self.start_time = datetime.now()
        thread = Process(target=self.run)
        thread.start()

    # Helpers
    def dummy(self):
        if not self.stop_request:
            self.stat_q.put({"type": StatType.DUMMY})

    def record_config(self, config):
        self.stat_q.put({"value": f"{config}", "type": StatType.CONFIG})

    def record_rtt(self, count):
        self.stat_q.put({"value": count, "type": StatType.RTT_COUNT})

    def record_query(self, count):
        self.stat_q.put({"value": count, "type": StatType.QUERY_COUNT})

    def record_network_latency(self, count):
        self.stat_q.put({"value": count, "type": StatType.NETWORK_LATENCY})

    def record_tx_try(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_TRY_COUNT})

    def record_tx_success(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_SUCCESS_COUNT})

    def record_tx_no_route(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_NO_ROUTE})

    def record_tx_fail(self):
        self.stat_q.put({"value": 1, "type": StatType.TX_FAIL_COUNT})

    def record_channel_reopen(self, count=1):
        self.stat_q.put({"value": count, "type": StatType.CHANNELS_REOPEN_COUNT})
