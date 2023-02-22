from .agent import Agent


def generate_agents(task_name, log_q, config):
    n = config["num_of_agents"]
    agents = []

    log_q.put({"task": task_name, "message": "Generating " + str(n) + " agents."})
    for i in range(n):
        agents.append(Agent(task_name, "agent_" + str(i), log_q, config))
    return agents
