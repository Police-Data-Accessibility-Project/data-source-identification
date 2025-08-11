import asyncio
from http import HTTPStatus
from typing import Dict

from fastapi import HTTPException
from pydantic import BaseModel

from src.db.client.async_ import AsyncDatabaseClient
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.exceptions import InvalidCollectorError
from src.collectors.mapping import COLLECTOR_MAPPING
from src.collectors.enums import CollectorType
from src.core.logger import AsyncCoreLogger
from src.core.function_trigger import FunctionTrigger


class AsyncCollectorManager:

    def __init__(
            self,
            logger: AsyncCoreLogger,
            adb_client: AsyncDatabaseClient,
            dev_mode: bool = False,
            post_collection_function_trigger: FunctionTrigger = None
    ):
        self.collectors: Dict[int, AsyncCollectorBase] = {}
        self.adb_client = adb_client
        self.logger = logger
        self.async_tasks: dict[int, asyncio.Task] = {}
        self.dev_mode = dev_mode
        self.post_collection_function_trigger = post_collection_function_trigger

    async def has_collector(self, cid: int) -> bool:
        return cid in self.collectors

    async def start_async_collector(
            self,
            collector_type: CollectorType,
            batch_id: int,
            dto: BaseModel,
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
                raise_error=True if self.dev_mode else False,
                post_collection_function_trigger=self.post_collection_function_trigger
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
        while self.async_tasks:
            cid, task = self.async_tasks.popitem()
            if task.done():
                try:
                    task.result()
                except Exception as e:
                    raise e
            else:
                task.cancel()
                try:
                    await task  # Await so cancellation propagates
                except asyncio.CancelledError:
                    pass