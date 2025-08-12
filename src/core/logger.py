import asyncio

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.log.pydantic.info import LogInfo


class AsyncCoreLogger:
    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        flush_interval: float = 10,
        batch_size: int = 100
    ):
        self.adb_client = adb_client
        self.flush_interval = flush_interval
        self.batch_size = batch_size

        self.log_queue = asyncio.Queue()
        self.lock = asyncio.Lock()
        self._flush_task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def __aenter__(self):
        self._stop_event.clear()
        self._flush_task = asyncio.create_task(self._flush_logs())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.shutdown()

    async def log(self, log_info: LogInfo):
        await self.log_queue.put(log_info)

    async def _flush_logs(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(self.flush_interval)
            await self.flush()

    async def flush(self):
        async with self.lock:
            logs: list[LogInfo] = []

            while not self.log_queue.empty() and len(logs) < self.batch_size:
                try:
                    log = self.log_queue.get_nowait()
                    logs.append(log)
                except asyncio.QueueEmpty:
                    break

            if logs:
                await self.adb_client.insert_logs(log_infos=logs)

    async def clear_log_queue(self):
        while not self.log_queue.empty():
            self.log_queue.get_nowait()

    async def flush_all(self):
        while not self.log_queue.empty():
            await self.flush()

    async def restart(self):
        await self.flush_all()
        await self.shutdown()
        self._stop_event.clear()
        self._flush_task = asyncio.create_task(self._flush_logs())

    async def shutdown(self):
        self._stop_event.set()
        if self._flush_task:
            await self._flush_task
        await self.flush_all()
