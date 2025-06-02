import asyncio


class AwaitableBarrier:
    def __init__(self):
        self._event = asyncio.Event()

    async def __call__(self, *args, **kwargs):
        await self._event.wait()

    def release(self):
        self._event.set()

