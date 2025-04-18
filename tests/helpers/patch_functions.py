from tests.helpers.AwaitableBarrier import AwaitableBarrier


async def block_sleep(monkeypatch) -> AwaitableBarrier:
    barrier = AwaitableBarrier()
    monkeypatch.setattr(
        "collector_manager.ExampleCollector.ExampleCollector.sleep",
        barrier
    )
    return barrier
