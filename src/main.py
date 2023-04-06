import sys
import os
from time import sleep
from simulation import Simulator, Status


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No config file specified. Exiting.")
        sys.exit(1)

    names = sys.argv[1:]

    # Simulators
    simulators = {}
    for name in names:
        simulator = Simulator(name)
        simulator.start()
        simulators[name] = simulator

    # User Commands
    while True:
        sleep(5)
        running = False
        os.system('clear')
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
        if not running:
            break
