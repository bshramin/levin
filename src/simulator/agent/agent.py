class Agent:
    task_name = ""
    name = ""
    log_q = None
    config = {}
    
    def __init__(self, task_name, name, log_q, config):
        self.task_name = task_name
        self.name = name
        self.log_q = log_q
        self.config = config
        self.log("Agent created.")

    def log(self, msg):
        self.log_q.put({"task": self.task_name, "message": self.name + ": " + msg})
