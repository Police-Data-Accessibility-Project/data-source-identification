"""
Base class for all collectors
"""
import abc
import threading
import time
from abc import ABC
from typing import Optional, Type

from pydantic import BaseModel

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.enums import BatchStatus
from core.preprocessors.PreprocessorBase import PreprocessorBase

class CollectorAbortException(Exception):
    pass

class CollectorBase(ABC):
    collector_type: CollectorType = None
    preprocessor: Type[PreprocessorBase] = None

    def __init__(
            self,
            batch_id: int,
            dto: BaseModel,
            logger: CoreLogger,
            db_client: DatabaseClient,
            raise_error: bool = False,
    ) -> None:
        self.batch_id = batch_id
        self.db_client = db_client
        self.dto = dto
        self.data: Optional[BaseModel] = None
        self.logger = logger
        self.status = BatchStatus.IN_PROCESS
        self.start_time = None
        self.compute_time = None
        self.raise_error = raise_error
        # # TODO: Determine how to update this in some of the other collectors
        self._stop_event = threading.Event()
        self.abort_ready = False

    @abc.abstractmethod
    def run_implementation(self) -> None:
        """
        This is the method that will be overridden by each collector
        No other methods should be modified except for this one.
        However, in each inherited class, new methods in addition to this one can be created
        Returns:

        """
        raise NotImplementedError

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.compute_time = time.time() - self.start_time

    def handle_error(self, e: Exception) -> None:
        if self.raise_error:
            raise e
        self.log(f"Error: {e}")

    def process(self) -> None:
        self.log("Processing collector...")
        preprocessor = self.preprocessor()
        url_infos = preprocessor.preprocess(self.data)
        self.log(f"URLs processed: {len(url_infos)}")

        self.log("Inserting URLs...")
        insert_urls_info: InsertURLsInfo = self.db_client.insert_urls(
            url_infos=url_infos,
            batch_id=self.batch_id
        )
        self.log("Updating batch...")
        self.db_client.update_batch_post_collection(
            batch_id=self.batch_id,
            total_url_count=insert_urls_info.total_count,
            duplicate_url_count=insert_urls_info.duplicate_count,
            original_url_count=insert_urls_info.original_count,
            batch_status=self.status,
            compute_time=self.compute_time
        )
        self.log("Done processing collector.")


    def run(self) -> None:
        try:
            self.start_timer()
            self.run_implementation()
            self.stop_timer()
            self.log("Collector completed successfully.")
            self.close()
            self.process()
        except CollectorAbortException:
            self.stop_timer()
            self.status = BatchStatus.ABORTED
        except Exception as e:
            self.stop_timer()
            self.status = BatchStatus.ERROR
            self.handle_error(e)

    def log(self, message: str) -> None:
        if self.abort_ready:
            raise CollectorAbortException
        self.logger.log(LogInfo(
            batch_id=self.batch_id,
            log=message
        ))

    def abort(self) -> None:
        self._stop_event.set()  # Signal the thread to stop
        self.log("Collector was aborted.")
        self.abort_ready = True

    def close(self) -> None:
        self._stop_event.set()
        self.status = BatchStatus.COMPLETE
