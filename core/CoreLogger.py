import asyncio
import threading
import queue
import time
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DatabaseClient import DatabaseClient


class CoreLogger:
    def __init__(self, flush_interval=10, db_client: DatabaseClient = DatabaseClient(), batch_size=100):
        self.db_client = db_client
        self.log_queue = asyncio.Queue()
        self.flush_interval = flush_interval
        self.batch_size = batch_size


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

    async def log(self, log_info: LogInfo):
        """
        Adds a log entry to the queue.
        """
        await self.log_queue.put(log_info)



    def flush_all(self):
        """
        Flushes all logs from the queue to the database.
        """
        while not self.log_queue.empty():
            self.flush()

    async def flush(self):
        """
        Flushes all logs from the queue to the database in batches.
        """
        logs: list[LogInfo] = []
        while not self.log_queue.empty() and len(logs) < self.batch_size:
            log = await self.log_queue.get()
            logs.append(log)
        if logs:
            try:
                await self.db_client.insert_logs(log_infos=logs)
            except Exception as e:
                # Handle logging database errors (e.g., save to fallback storage)
                print(f"Error while flushing logs: {e}")

    async def shutdown(self):
        """
        Stops the logger gracefully and flushes any remaining logs.
        """
        self.flush_all()  # Flush remaining logs
