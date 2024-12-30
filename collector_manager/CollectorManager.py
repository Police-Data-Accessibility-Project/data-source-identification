"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""
import asyncio
import threading
from typing import Dict, List

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
        self.tasks: Dict[int, asyncio.Task] = {}
        self.logger = logger

    def list_collectors(self) -> List[str]:
        return [cm.value for cm in list(COLLECTOR_MAPPING.keys())]

    async def start_collector(
            self,
            collector_type: CollectorType,
            batch_id: int,
            dto: BaseModel,
            raise_error: bool = False
    ) -> None:
        if batch_id in self.collectors:
            raise ValueError(f"Collector with batch_id {batch_id} is already running.")
        try:
            collector_class = COLLECTOR_MAPPING[collector_type]
            collector = collector_class(batch_id=batch_id, dto=dto, logger=self.logger, raise_error=raise_error)
        except KeyError:
            raise InvalidCollectorError(f"Collector {collector_type.value} not found.")
        self.collectors[batch_id] = collector
        self.collectors[batch_id] = collector
        task = asyncio.create_task(collector.run())
        self.tasks[batch_id] = task

    def get_info(self, cid: str) -> str:
        collector = self.collectors.get(cid)
        if not collector:
            return f"Collector with CID {cid} not found."
        logs = "\n".join(collector.logs[-3:])  # Show the last 3 logs
        return f"{cid} ({collector.name}) - {collector.status}\nLogs:\n{logs}"

    async def close_collector(self, cid: int) -> CollectorCloseInfo:
        collector = self.try_getting_collector(cid)
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

    async def shutdown_all_collectors(self) -> None:
        for batch_id in list(self.collectors.keys()):
            await self.close_collector(batch_id)
