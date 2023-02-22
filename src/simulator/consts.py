from enum import Enum


class Status(Enum):
    NOT_INITIALIZED = 1
    WAITING = 2
    RUNNING = 3
    STOPPED = 4
