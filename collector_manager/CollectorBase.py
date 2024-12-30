"""
Base class for all collectors
"""
import abc
import asyncio
import threading
import time
from abc import ABC
from typing import Optional

from pydantic import BaseModel

from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.DTOs.CollectorCloseInfo import CollectorCloseInfo
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.enums import BatchStatus
from core.exceptions import InvalidPreprocessorError
from core.preprocessors.PreprocessorBase import PreprocessorBase
from core.preprocessors.preprocessor_mapping import PREPROCESSOR_MAPPING


class CollectorBase(ABC):
    collector_type: CollectorType = None

    def __init__(
            self,
            batch_id: int,
            dto: BaseModel,
            logger: CoreLogger,
            raise_error: bool = False) -> None:
        self.batch_id = batch_id
        self.dto = dto
        self.data: Optional[BaseModel] = None
        self.logger = logger
        self.status = BatchStatus.IN_PROCESS
        self.start_time = None
        self.compute_time = None
        self.raise_error = raise_error
        # # TODO: Determine how to update this in some of the other collectors
        self._stop_event = asyncio.Event()

    @abc.abstractmethod
    async def run_implementation(self) -> None:
        raise NotImplementedError

    async def start_timer(self) -> None:
        self.start_time = asyncio.get_event_loop().time()

    async def stop_timer(self) -> None:
        self.compute_time = asyncio.get_event_loop().time() - self.start_time

    async def handle_error(self, e: Exception) -> None:
        if self.raise_error:
            raise e
        await self.log(f"Error: {e}")

    @staticmethod
    def get_preprocessor(
            collector_type: CollectorType
    ) -> PreprocessorBase:
        # TODO: Look into just having the preprocessor in the collector
        try:
            return PREPROCESSOR_MAPPING[collector_type]()
        except KeyError:
            raise InvalidPreprocessorError(f"Preprocessor for {collector_type} not found.")

    async def process(self, close_info: CollectorCloseInfo) -> None:
        db_client = DatabaseClient()
        await self.log("Processing collector...")
        batch_status = close_info.status
        preprocessor = self.get_preprocessor(close_info.collector_type)
        url_infos = preprocessor.preprocess(close_info.data)
        await self.log(f"URLs processed: {len(url_infos)}")

        await self.log("Inserting URLs...")
        insert_urls_info = db_client.insert_urls(
            url_infos=url_infos,
            batch_id=close_info.batch_id
        )
        await self.log("Updating batch...")
        db_client.update_batch_post_collection(
            batch_id=close_info.batch_id,
            total_url_count=insert_urls_info.total_count,
            duplicate_url_count=insert_urls_info.duplicate_count,
            original_url_count=insert_urls_info.original_count,
            batch_status=batch_status,
            compute_time=close_info.compute_time
        )
        db_client.add_duplicate_info(insert_urls_info.duplicates)
        await self.log("Done processing collector.")


    async def run(self) -> None:
        try:
            await self.start_timer()
            await self.run_implementation()
            await self.stop_timer()
            self.status = BatchStatus.COMPLETE
            await self.log("Collector completed successfully.")
            await self.process(
                close_info=self.close()
            )
        except Exception as e:
            await self.stop_timer()
            self.status = BatchStatus.ERROR
            await self.handle_error(e)

    async def log(self, message: str) -> None:
        await self.logger.log(LogInfo(
            batch_id=self.batch_id,
            log=message
        ))

    def abort(self) -> CollectorCloseInfo:
        self._stop_event.set()
        return CollectorCloseInfo(
            batch_id=self.batch_id,
            status=BatchStatus.ABORTED,
            message="Collector aborted.",
            compute_time=self.compute_time,
            collector_type=self.collector_type
        )

    def close(self):
        self._stop_event.set()
        return CollectorCloseInfo(
            batch_id=self.batch_id,
            status=BatchStatus.COMPLETE,
            data=self.data,
            message="Collector closed and data harvested successfully.",
            compute_time=self.compute_time,
            collector_type=self.collector_type
        )
