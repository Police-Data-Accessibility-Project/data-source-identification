

import threading
import queue
import time
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor

from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DatabaseClient import DatabaseClient


class CoreLogger:
    def __init__(
            self,
            db_client: DatabaseClient,
            flush_interval=10,
            batch_size=100
    ):
        self.db_client = db_client
        self.flush_interval = flush_interval
        self.batch_size = batch_size

        self.log_queue = queue.Queue()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        # Start the periodic flush task
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.flush_future: Future = self.executor.submit(self._flush_logs)

    def __enter__(self):
        """
        Start the logger for use in a context.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Gracefully shut down the logger when exiting the context.
        """
        self.shutdown()

    def log(self, log_info: LogInfo):
        """
        Adds a log entry to the queue.
        """
        self.log_queue.put(log_info)

    def _flush_logs(self):
        """
        Periodically flushes logs from the queue to the database.
        """
        while not self.stop_event.is_set():
            time.sleep(self.flush_interval)
            self.flush()

    def flush(self):
        """
        Flushes all logs from the queue to the database in batches.
        """
        with self.lock:
            logs: list[LogInfo] = []
            while not self.log_queue.empty() and len(logs) < self.batch_size:
                try:
                    log = self.log_queue.get_nowait()
                    logs.append(log)
                except queue.Empty:
                    break

            if logs:
                try:
                    self.db_client.insert_logs(log_infos=logs)
                except Exception as e:
                    # Handle logging database errors (e.g., save to fallback storage)
                    print(f"Error while flushing logs: {e}")

    def flush_all(self):
        """
        Flushes all logs from the queue to the database.
        """
        while not self.log_queue.empty():
            self.flush()

    def restart(self):
        self.flush_all()
        self.executor.shutdown(wait=False)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.flush_future = self.executor.submit(self._flush_logs)

    def shutdown(self):
        """
        Stops the logger gracefully and flushes any remaining logs.
        """
        self.stop_event.set()
        if self.flush_future and not self.flush_future.done():
            self.flush_future.result(timeout=10)
        self.flush_all()  # Flush remaining logs
