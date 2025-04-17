import abc
import asyncio
import time
from abc import ABC
from typing import Type, Optional

from pydantic import BaseModel

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_manager.enums import CollectorType
from core.AsyncCoreLogger import AsyncCoreLogger
from core.FunctionTrigger import FunctionTrigger
from core.enums import BatchStatus
from core.preprocessors.PreprocessorBase import PreprocessorBase


class AsyncCollectorBase(ABC):
    collector_type: CollectorType = None
    preprocessor: Type[PreprocessorBase] = None


    def __init__(
            self,
            batch_id: int,
            dto: BaseModel,
            logger: AsyncCoreLogger,
            adb_client: AsyncDatabaseClient,
            raise_error: bool = False,
            post_collection_function_trigger: Optional[FunctionTrigger] = None,
    ) -> None:
        self.post_collection_function_trigger = post_collection_function_trigger
        self.batch_id = batch_id
        self.adb_client = adb_client
        self.dto = dto
        self.data: Optional[BaseModel] = None
        self.logger = logger
        self.status = BatchStatus.IN_PROCESS
        self.start_time = None
        self.compute_time = None
        self.raise_error = raise_error

    @abc.abstractmethod
    async def run_implementation(self) -> None:
        """
        This is the method that will be overridden by each collector
        No other methods should be modified except for this one.
        However, in each inherited class, new methods in addition to this one can be created
        Returns:

        """
        raise NotImplementedError

    async def start_timer(self) -> None:
        self.start_time = time.time()

    async def stop_timer(self) -> None:
        self.compute_time = time.time() - self.start_time

    async def handle_error(self, e: Exception) -> None:
        if self.raise_error:
            raise e
        await self.log(f"Error: {e}")
        await self.adb_client.update_batch_post_collection(
            batch_id=self.batch_id,
            batch_status=self.status,
            compute_time=self.compute_time,
            total_url_count=0,
            original_url_count=0,
            duplicate_url_count=0
        )

    async def process(self) -> None:
        await self.log("Processing collector...", allow_abort=False)
        preprocessor = self.preprocessor()
        url_infos = preprocessor.preprocess(self.data)
        await self.log(f"URLs processed: {len(url_infos)}", allow_abort=False)

        await self.log("Inserting URLs...", allow_abort=False)
        insert_urls_info: InsertURLsInfo = await self.adb_client.insert_urls(
            url_infos=url_infos,
            batch_id=self.batch_id
        )
        await self.log("Updating batch...", allow_abort=False)
        await self.adb_client.update_batch_post_collection(
            batch_id=self.batch_id,
            total_url_count=insert_urls_info.total_count,
            duplicate_url_count=insert_urls_info.duplicate_count,
            original_url_count=insert_urls_info.original_count,
            batch_status=self.status,
            compute_time=self.compute_time
        )
        await self.log("Done processing collector.", allow_abort=False)

        if self.post_collection_function_trigger is not None:
            await self.post_collection_function_trigger.trigger_or_rerun()

    async def run(self) -> None:
        try:
            await self.start_timer()
            await self.run_implementation()
            await self.stop_timer()
            await self.log("Collector completed successfully.")
            await self.close()
            await self.process()
        except asyncio.CancelledError:
            await self.stop_timer()
            self.status = BatchStatus.ABORTED
            await self.adb_client.update_batch_post_collection(
                batch_id=self.batch_id,
                batch_status=BatchStatus.ABORTED,
                compute_time=self.compute_time,
                total_url_count=0,
                original_url_count=0,
                duplicate_url_count=0
            )
        except Exception as e:
            await self.stop_timer()
            self.status = BatchStatus.ERROR
            await self.handle_error(e)

    async def log(
            self,
            message: str,
            allow_abort = True  # Deprecated
    ) -> None:
        await self.logger.log(LogInfo(
            batch_id=self.batch_id,
            log=message
        ))

    async def close(self) -> None:
        self.status = BatchStatus.READY_TO_LABEL
