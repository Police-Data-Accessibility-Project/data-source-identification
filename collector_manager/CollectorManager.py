"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict, List

from pydantic import BaseModel

from collector_db.DatabaseClient import DatabaseClient
from collector_manager.CollectorBase import CollectorBase
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger


class InvalidCollectorError(Exception):
    pass

# Collector Manager Class
class CollectorManager:
    def __init__(
            self,
            logger: CoreLogger,
            db_client: DatabaseClient,
            dev_mode: bool = False,
            max_workers: int = 10  # Limit the number of concurrent threads
    ):
        self.collectors: Dict[int, CollectorBase] = {}
        self.futures: Dict[int, Future] = {}
        self.threads: Dict[int, threading.Thread] = {}
        self.db_client = db_client
        self.logger = logger
        self.lock = threading.Lock()
        self.max_workers = max_workers
        self.dev_mode = dev_mode
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def restart_executor(self):
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    def list_collectors(self) -> List[str]:
        return [cm.value for cm in list(COLLECTOR_MAPPING.keys())]

    def start_collector(
            self,
            collector_type: CollectorType,
            batch_id: int,
            dto: BaseModel
    ) -> None:
        with self.lock:
            # If executor is shutdown, restart it
            if self.executor._shutdown:
                self.restart_executor()

            if batch_id in self.collectors:
                raise ValueError(f"Collector with batch_id {batch_id} is already running.")
            try:
                collector_class = COLLECTOR_MAPPING[collector_type]
                collector = collector_class(
                    batch_id=batch_id,
                    dto=dto,
                    logger=self.logger,
                    db_client=self.db_client,
                    raise_error=True if self.dev_mode else False
                )
            except KeyError:
                raise InvalidCollectorError(f"Collector {collector_type.value} not found.")
            self.collectors[batch_id] = collector

            future = self.executor.submit(collector.run)
            self.futures[batch_id] = future

            # thread = threading.Thread(target=collector.run)
            # self.threads[batch_id] = thread
            # thread.start()

    def get_info(self, cid: str) -> str:
        collector = self.collectors.get(cid)
        if not collector:
            return f"Collector with CID {cid} not found."
        logs = "\n".join(collector.logs[-3:])  # Show the last 3 logs
        return f"{cid} ({collector.name}) - {collector.status}\nLogs:\n{logs}"


    def try_getting_collector(self, cid):
        collector = self.collectors.get(cid)
        if collector is None:
            raise InvalidCollectorError(f"Collector with CID {cid} not found.")
        return collector

    def abort_collector(self, cid: int) -> None:
        collector = self.try_getting_collector(cid)
        # Get collector thread
        thread = self.threads.get(cid)
        future = self.futures.get(cid)
        collector.abort()
        # thread.join(timeout=1)
        self.collectors.pop(cid)
        self.futures.pop(cid)
        # self.threads.pop(cid)

    def shutdown_all_collectors(self) -> None:
        with self.lock:
            for cid, future in self.futures.items():
                if future.done():
                    try:
                        future.result()
                    except Exception as e:
                        raise e
                self.collectors[cid].abort()

            self.executor.shutdown(wait=True)
            self.collectors.clear()
            self.futures.clear()