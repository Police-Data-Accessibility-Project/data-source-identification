"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""
import threading
from typing import Dict, List, Optional

from pydantic import BaseModel

from collector_manager.CollectorBase import CollectorBase
from collector_manager.DTOs.CollectorCloseInfo import CollectorCloseInfo
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.enums import BatchStatus


class InvalidCollectorError(Exception):
    pass

# Collector Manager Class
class CollectorManager:
    def __init__(
            self,
            logger: CoreLogger
    ):
        self.collectors: Dict[int, CollectorBase] = {}
        self.threads: Dict[int, threading.Thread] = {}
        self.logger = logger
        self.lock = threading.Lock()

    def list_collectors(self) -> List[str]:
        return [cm.value for cm in list(COLLECTOR_MAPPING.keys())]

    def start_collector(
            self,
            collector_type: CollectorType,
            batch_id: int,
            dto: BaseModel
    ) -> None:
        with self.lock:
            if batch_id in self.collectors:
                raise ValueError(f"Collector with batch_id {batch_id} is already running.")
            try:
                collector_class = COLLECTOR_MAPPING[collector_type]
                collector = collector_class(batch_id=batch_id, dto=dto, logger=self.logger)
            except KeyError:
                raise InvalidCollectorError(f"Collector {collector_type.value} not found.")
            self.collectors[batch_id] = collector
            thread = threading.Thread(target=collector.run, daemon=True)
            self.threads[batch_id] = thread
            thread.start()

    def get_info(self, cid: str) -> str:
        collector = self.collectors.get(cid)
        if not collector:
            return f"Collector with CID {cid} not found."
        logs = "\n".join(collector.logs[-3:])  # Show the last 3 logs
        return f"{cid} ({collector.name}) - {collector.status}\nLogs:\n{logs}"

    def close_collector(self, cid: int) -> CollectorCloseInfo:
        collector = self.try_getting_collector(cid)
        with self.lock:
            match collector.status:
                case BatchStatus.IN_PROCESS:
                    close_info = collector.abort()
                case BatchStatus.COMPLETE:
                    close_info = collector.close()
                case _:
                    raise ValueError(f"Cannot close collector {cid} with status {collector.status}.")
            del self.collectors[cid]
            self.threads.pop(cid, None)
            return close_info


    def try_getting_collector(self, cid):
        collector = self.collectors.get(cid)
        if collector is None:
            raise InvalidCollectorError(f"Collector with CID {cid} not found.")
        return collector

    def shutdown_all_collectors(self) -> None:
        with self.lock:
            for cid, collector in self.collectors.items():
                collector.abort()
            for thread in self.threads.values():
                thread.join()
            self.collectors.clear()
            self.threads.clear()