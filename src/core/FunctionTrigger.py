import asyncio
from typing import Callable, Awaitable

class FunctionTrigger:
    """
    A small class used to trigger a function to run in a loop
    If the trigger is used again while the task is running, the task will be rerun
    """

    def __init__(self, func: Callable[[], Awaitable[None]]):
        self._func = func
        self._lock = asyncio.Lock()
        self._rerun_requested = False
        self._loop_running = False

    async def trigger_or_rerun(self):
        if self._loop_running:
            self._rerun_requested = True
            return

        async with self._lock:
            self._loop_running = True
            try:
                while True:
                    self._rerun_requested = False
                    await self._func()
                    if not self._rerun_requested:
                        break
            finally:
                self._loop_running = False
