import asyncio
from http import HTTPStatus
from typing import Dict

from fastapi import HTTPException
from pydantic import BaseModel

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_manager.AsyncCollectorBase import AsyncCollectorBase
from collector_manager.CollectorManager import InvalidCollectorError
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger


class AsyncCollectorManager:

    def __init__(
            self,
            logger: CoreLogger,
            adb_client: AsyncDatabaseClient,
            dev_mode: bool = False
    ):
        self.collectors: Dict[int, AsyncCollectorBase] = {}
        self.adb_client = adb_client
        self.logger = logger
        self.async_tasks: dict[int, asyncio.Task] = {}
        self.dev_mode = dev_mode

    async def has_collector(self, cid: int) -> bool:
        return cid in self.collectors

    async def start_async_collector(
            self,
            collector_type: CollectorType,
            batch_id: int,
            dto: BaseModel
    ) -> None:
        if batch_id in self.collectors:
            raise ValueError(f"Collector with batch_id {batch_id} is already running.")
        try:
            collector_class = COLLECTOR_MAPPING[collector_type]
            collector = collector_class(
                batch_id=batch_id,
                dto=dto,
                logger=self.logger,
                adb_client=self.adb_client,
                raise_error=True if self.dev_mode else False
            )
        except KeyError:
            raise InvalidCollectorError(f"Collector {collector_type.value} not found.")

        self.collectors[batch_id] = collector

        task = asyncio.create_task(collector.run())
        self.async_tasks[batch_id] = task

    def try_getting_collector(self, cid):
        collector = self.collectors.get(cid)
        if collector is None:
            raise InvalidCollectorError(f"Collector with CID {cid} not found.")
        return collector

    async def abort_collector_async(self, cid: int) -> None:
        task = self.async_tasks.get(cid)
        if not task:
            raise HTTPException(status_code=HTTPStatus.OK, detail="Task not found")
        if task is not None:
            task.cancel()
        try:
            await task  # Await so cancellation propagates
        except asyncio.CancelledError:
            pass

        self.async_tasks.pop(cid)

    async def shutdown_all_collectors(self) -> None:
        for cid, task in self.async_tasks.items():
            if task.done():
                try:
                    task.result()
                except Exception as e:
                    raise e
            await self.abort_collector_async(cid)