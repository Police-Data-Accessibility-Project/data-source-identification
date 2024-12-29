"""
Base class for all collectors
"""
import abc
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
        self._stop_event = threading.Event()

    @abc.abstractmethod
    def run_implementation(self) -> None:
        raise NotImplementedError

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.compute_time = time.time() - self.start_time

    def handle_error(self, e: Exception) -> None:
        if self.raise_error:
            raise e
        self.log(f"Error: {e}")

    @staticmethod
    def get_preprocessor(
            collector_type: CollectorType
    ) -> PreprocessorBase:
        # TODO: Look into just having the preprocessor in the collector
        try:
            return PREPROCESSOR_MAPPING[collector_type]()
        except KeyError:
            raise InvalidPreprocessorError(f"Preprocessor for {collector_type} not found.")

    def process(self, close_info: CollectorCloseInfo) -> None:
        db_client = DatabaseClient()
        self.log("Processing collector...")
        batch_status = close_info.status
        preprocessor = self.get_preprocessor(close_info.collector_type)
        url_infos = preprocessor.preprocess(close_info.data)
        self.log(f"URLs processed: {len(url_infos)}")
        db_client.update_batch_post_collection(
            batch_id=close_info.batch_id,
            url_count=len(url_infos),
            batch_status=batch_status,
            compute_time=close_info.compute_time
        )
        self.log("Inserting URLs...")
        insert_urls_info = db_client.insert_urls(
            url_infos=url_infos,
            batch_id=close_info.batch_id
        )
        self.log("Inserting duplicates...")
        db_client.add_duplicate_info(insert_urls_info.duplicates)
        self.log("Done processing collector.")


    def run(self) -> None:
        try:
            self.start_timer()
            self.run_implementation()
            self.stop_timer()
            self.status = BatchStatus.COMPLETE
            self.log("Collector completed successfully.")
            self.process(
                close_info=self.close()
            )
        except Exception as e:
            self.stop_timer()
            self.status = BatchStatus.ERROR
            self.handle_error(e)

    def log(self, message: str) -> None:
        self.logger.log(LogInfo(
            batch_id=self.batch_id,
            log=message
        ))

    def abort(self) -> CollectorCloseInfo:
        self._stop_event.set()
        self.stop_timer()
        return CollectorCloseInfo(
            batch_id=self.batch_id,
            status=BatchStatus.ABORTED,
            message="Collector aborted.",
            compute_time=self.compute_time,
            collector_type=self.collector_type
        )

    def close(self):
        compute_time = self.compute_time
        self._stop_event.set()
        return CollectorCloseInfo(
            batch_id=self.batch_id,
            status=BatchStatus.COMPLETE,
            data=self.data,
            message="Collector closed and data harvested successfully.",
            compute_time=compute_time,
            collector_type=self.collector_type
        )
