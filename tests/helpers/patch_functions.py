from tests.helpers.awaitable_barrier import AwaitableBarrier


async def block_sleep(monkeypatch) -> AwaitableBarrier:
    barrier = AwaitableBarrier()
    monkeypatch.setattr(
        "src.collectors.source_collectors.example.core.ExampleCollector.sleep",
        barrier
    )
    return barrier
