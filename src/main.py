import sys
from queue import Empty
from multiprocessing import Manager
from time import sleep
from simulation import Simulator, Status


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No config file specified. Exiting.")
        sys.exit(1)

    names = sys.argv[1:]

    manager = Manager()
    q = manager.Queue()
    # Simulators
    simulators = {}
    for name in names:
        simulator = Simulator(name, q)
        simulator.start()
        simulators[name] = simulator

    done_simulators_num = 0
    # User Commands
    while True:
        sleep(10)

        try:
            line = q.get_nowait()
            if line == "done":
                done_simulators_num += 1
        except Empty:
            pass
        if done_simulators_num == len(simulators):
            break
        for simulator in simulators:
            if simulators[simulator].status != Status.STOPPED:
                running = True
            print("Simulator " + simulator + ": " + simulators[simulator].status.name)
            for agent in simulators[simulator].agents:
                print(
                    "   Agent "
                    + str(agent.id)
                    + ": "
                    + agent.status.name
                    + ", transactions: "
                    + str(agent.total_transactions)
                )

    print("All simulators finished.")
