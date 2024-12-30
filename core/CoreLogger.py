

import threading
import queue
import time
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DatabaseClient import DatabaseClient


class CoreLogger:
    def __init__(self, flush_interval=10, db_client: DatabaseClient = DatabaseClient(), batch_size=100):
        self.db_client = db_client
        self.log_queue = queue.Queue()
        self.lock = threading.Lock()
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.stop_event = threading.Event()

        # Start the flush thread
        self.flush_thread = threading.Thread(target=self._flush_logs)
        self.flush_thread.start()

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

    def flush_all(self):
        """
        Flushes all logs from the queue to the database.
        """
        while not self.log_queue.empty():
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

    def shutdown(self):
        """
        Stops the logger gracefully and flushes any remaining logs.
        """
        self.stop_event.set()
        self.flush_thread.join(timeout=1)
        self.flush()  # Flush remaining logs
