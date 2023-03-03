import sys
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
        print("Enter command (e)xit,(l)ist:")
        command = input()
        if command == "e" or command == "exit":
            break
        if command == "l" or command == "list":
            for simulator in simulators:
                print(simulator + ": " + simulators[simulator].status.name)
                for agent in simulators[simulator].agents:
                    print(
                        "    Agent "
                        + str(agent.id)
                        + ": "
                        + agent.status.name
                        + ", transactions: "
                        + str(agent.total_transactions)
                    )

    # Stopping threads and ending the program

    for simulator in simulators:
        simulators[simulator].stop_request = True
    for simulator in simulators:
        while simulators[simulator].status != Status.STOPPED:
            sleep(0.1)
