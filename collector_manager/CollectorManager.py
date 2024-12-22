"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""

import threading
import uuid
from typing import Dict, List, Optional

from collector_manager.ExampleCollector import ExampleCollector
from collector_manager.enums import Status


# Collector Manager Class
class CollectorManager:
    def __init__(self):
        self.collectors: Dict[str, ExampleCollector] = {}

    def list_collectors(self) -> List[str]:
        return ["example_collector"]

    def start_collector(
            self,
            name: str,
            config: Optional[dict] = None
    ) -> str:
        cid = str(uuid.uuid4())
        # The below would need to become more sophisticated
        # As we may load different collectors depending on the name
        collector = ExampleCollector(name, config)
        self.collectors[cid] = collector
        thread = threading.Thread(target=collector.run, daemon=True)
        thread.start()
        return cid

    def get_status(self, cid: Optional[str] = None) -> str | List[str]:
        if cid:
            collector = self.collectors.get(cid)
            if not collector:
                return f"Collector with CID {cid} not found."
            return f"{cid} ({collector.name}) - {collector.status}"
        else:
            return [
                f"{cid} ({collector.name}) - {collector.status}"
                for cid, collector in self.collectors.items()
            ]

    def get_info(self, cid: str) -> str:
        collector = self.collectors.get(cid)
        if not collector:
            return f"Collector with CID {cid} not found."
        logs = "\n".join(collector.logs[-3:])  # Show the last 3 logs
        return f"{cid} ({collector.name}) - {collector.status}\nLogs:\n{logs}"

    def close_collector(self, cid: str) -> str:
        collector = self.collectors.get(cid)
        if not collector:
            return f"Collector with CID {cid} not found."
        match collector.status:
            case Status.RUNNING:
                collector.stop()
                return f"Collector {cid} stopped."
            case Status.COMPLETED:
                data = collector.data
                del self.collectors[cid]
                return f"Collector {cid} harvested. Data: {data}"
            case _:
                return f"Cannot close collector {cid} with status {collector.status}."

