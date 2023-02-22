import sys
from queue import Queue
from simulator import Simulator, Status
from logger import Logger


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No config file specified. Exiting.")
        sys.exit(1)

    names = sys.argv[1:]

    # Logging
    # IDEA: To improve performance each simulator can have it's own logger.
    logger_q = Queue(maxsize=1000)
    logger = Logger(logger_q, names)
    logger.start()

    # Simulators
    simulators = {}
    for name in names:
        simulator = Simulator(name, logger_q)
        simulator.start()
        simulators[name] = simulator

    # User Commands
    while True:
        print("Enter command (e)xit,(l)ist:")
        command = input()
        if command == "e" or command == "exit":
            for simulator in simulators:
                simulators[simulator].in_q.put("stop")
            for simulator in simulators:
                simulators[simulator].out_q.get()
            logger.in_q.put("stop")
            logger.out_q.get()
            sys.exit(0)

        if command == "l" or command == "list":
            for simulator in simulators:
                simulators[simulator].in_q.put("status")
            for simulator in simulators:
                print(simulator + ": " + Status(simulators[simulator].out_q.get()).name)
