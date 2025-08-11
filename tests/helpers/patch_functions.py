from tests.helpers.awaitable_barrier import AwaitableBarrier


async def block_sleep(monkeypatch) -> AwaitableBarrier:
    barrier = AwaitableBarrier()
    monkeypatch.setattr(
        "src.collectors.impl.example.core.ExampleCollector.sleep",
        barrier
    )
    return barrier
