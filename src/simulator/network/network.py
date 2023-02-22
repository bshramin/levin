import networkx as nx


class Network:
    name = ""
    log_q = None
    graph = None

    def __init__(self, name, log_q, network_config):
        self.name = name
        self.log_q = log_q
        self.graph = self.build_graph_from_config(network_config)

    def build_graph_from_config(self, nc):
        if nc["topology"] == "random":
            return self.build_random_graph(nc)
        elif nc["topology"] == "star":
            raise NotImplementedError
        elif nc["topology"] == "complete":
            raise NotImplementedError

    def build_random_graph(self, nc):
        raise NotImplementedError

    def log(self, msg):
        self.log_q.put({"task": self.name, "message": msg})
