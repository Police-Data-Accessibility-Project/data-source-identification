"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""
import json
import threading
import uuid
from typing import Dict, List, Optional, Type

from pydantic import BaseModel

from collector_manager.CollectorBase import CollectorBase, CollectorCloseInfo
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import CollectorStatus, CollectorType


class InvalidCollectorError(Exception):
    pass

# Collector Manager Class
class CollectorManager:
    def __init__(self):
        self.collectors: Dict[int, CollectorBase] = {}

    def list_collectors(self) -> List[str]:
        return [cm.value for cm in list(COLLECTOR_MAPPING.keys())]

    def start_collector(
            self,
            collector: CollectorBase,
            cid: int
    ) -> None:

        self.collectors[cid] = collector
        thread = threading.Thread(target=collector.run, daemon=True)
        thread.start()

    def get_status(self, cid: Optional[str] = None) -> str | List[str]:
        if cid:
            collector = self.collectors.get(cid)
            if not collector:
                return f"Collector with CID {cid} not found."
            return f"{cid} ({collector.name}) - {collector.status.value}"
        else:
            return [
                f"{cid} ({collector.name}) - {collector.status.value}"
                for cid, collector in self.collectors.items()
            ]

    def get_info(self, cid: str) -> str:
        collector = self.collectors.get(cid)
        if not collector:
            return f"Collector with CID {cid} not found."
        logs = "\n".join(collector.logs[-3:])  # Show the last 3 logs
        return f"{cid} ({collector.name}) - {collector.status}\nLogs:\n{logs}"

    def close_collector(self, cid: int) -> CollectorCloseInfo:
        collector = self.try_getting_collector(cid)
        match collector.status:
            case CollectorStatus.RUNNING:
                return collector.abort()
            case CollectorStatus.COMPLETED:
                close_info = collector.close()
                del self.collectors[cid]
                return close_info
            case _:
                raise ValueError(f"Cannot close collector {cid} with status {collector.status}.")

    def try_getting_collector(self, cid):
        collector = self.collectors.get(cid)
        if collector is None:
            raise InvalidCollectorError(f"Collector with CID {cid} not found.")
        return collector

