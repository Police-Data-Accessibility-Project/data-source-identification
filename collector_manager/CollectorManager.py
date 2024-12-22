"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""
import json
import threading
import uuid
from typing import Dict, List, Optional

from collector_manager.CollectorBase import CollectorBase
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import Status


class InvalidCollectorError(Exception):
    pass

# Collector Manager Class
class CollectorManager:
    def __init__(self):
        self.collectors: Dict[str, CollectorBase] = {}

    def list_collectors(self) -> List[str]:
        return list(COLLECTOR_MAPPING.keys())

    def start_collector(
            self,
            name: str,
            config: Optional[dict] = None
    ) -> str:
        cid = str(uuid.uuid4())
        try:
            collector = COLLECTOR_MAPPING[name](name, config)
        except KeyError:
            raise ValueError(f"Collector {name} not found.")

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
        # TODO: Extract logic
        if not collector:
            return f"Collector with CID {cid} not found."
        match collector.status:
            case Status.RUNNING:
                collector.stop()
                return f"Collector {cid} stopped."
            case Status.COMPLETED:
                close_info = collector.close()
                name = collector.name
                del self.collectors[cid]
                if close_info.error_msg is not None:
                    data = close_info.data
                    with open(f"{name}_{cid}.json", "w", encoding='utf-8') as f:
                        json.dump(obj=data, fp=f, ensure_ascii=False, indent=4)
                    return f"Error closing collector {cid}: {close_info.error_msg}"
                # Write data to file
                data = close_info.data
                with open(f"{name}_{cid}.json", "w") as f:
                    json.dump(data, f, indent=4)

                return f"Collector {cid} harvested. Data: {data}"
            case _:
                return f"Cannot close collector {cid} with status {collector.status}."

