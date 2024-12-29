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
from collector_manager.enums import CollectorStatus, CollectorType
from core.CoreLogger import CoreLogger
from core.DTOs.CollectorStatusInfo import CollectorStatusInfo


class InvalidCollectorError(Exception):
    pass

# Collector Manager Class
class CollectorManager:
    def __init__(
            self,
            logger: CoreLogger
    ):
        self.collectors: Dict[int, CollectorBase] = {}
        self.logger = logger

    def list_collectors(self) -> List[str]:
        return [cm.value for cm in list(COLLECTOR_MAPPING.keys())]

    def start_collector(
            self,
            collector_type: CollectorType,
            batch_id: int,
            dto: BaseModel
    ) -> None:
        try:
            collector_class: type[CollectorBase] = COLLECTOR_MAPPING[collector_type]
            collector = collector_class(
                batch_id=batch_id,
                dto=dto,
                logger=self.logger,
            )
        except KeyError:
            raise InvalidCollectorError(f"Collector {collector_type.value} not found.")

        self.collectors[collector.batch_id] = collector
        thread = threading.Thread(target=collector.run, daemon=True)
        thread.start()

    def get_status(
            self,
            batch_id: Optional[int] = None
    ) -> CollectorStatusInfo | List[CollectorStatusInfo]:
        if batch_id:
            collector = self.collectors.get(batch_id)
            if not collector:
                # TODO: Test this logic
                raise InvalidCollectorError(f"Collector with CID {batch_id} not found.")
            return CollectorStatusInfo(
                batch_id=batch_id,
                collector_type=collector.collector_type,
                status=collector.status,
            )
        else:
            # TODO: Test this logic.
            results = []
            for cid, collector in self.collectors.items():
                results.append(CollectorStatusInfo(
                    batch_id=cid,
                    collector_type=collector.collector_type,
                    status=collector.status,
                ))
            return results


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

