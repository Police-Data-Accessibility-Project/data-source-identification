"""
Base class for all collectors
"""
import abc
import threading
from abc import ABC

from collector_manager.enums import Status


class CollectorBase(ABC):
    def __init__(self, name: str, config: dict) -> None:
        self.name = name
        self.config = config
        self.data = {}
        self.logs = []
        self.status = Status.RUNNING
        # # TODO: Determine how to update this in some of the other collectors
        self._stop_event = threading.Event()

    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    def log(self, message: str) -> None:
        self.logs.append(message)

    def stop(self) -> None:
        self._stop_event.set()