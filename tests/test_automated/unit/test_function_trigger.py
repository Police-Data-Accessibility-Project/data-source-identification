import asyncio
from collections import deque

import pytest

from core.FunctionTrigger import FunctionTrigger


@pytest.mark.asyncio
async def test_single_run():
    calls = []

    async def task_fn():
        calls.append("run")
        await asyncio.sleep(0.01)

    trigger = FunctionTrigger(task_fn)

    await trigger.trigger_or_rerun()

    assert calls == ["run"]

@pytest.mark.asyncio
async def test_rerun_requested():
    call_log = deque()

    async def task_fn():
        call_log.append("start")
        await asyncio.sleep(0.01)
        call_log.append("end")

    trigger = FunctionTrigger(task_fn)

    # Start first run
    task = asyncio.create_task(trigger.trigger_or_rerun())

    await asyncio.sleep(0.005)  # Ensure it's in the middle of first run
    await trigger.trigger_or_rerun()  # This should request a rerun

    await task

    # One full loop with rerun should call twice
    assert list(call_log) == ["start", "end", "start", "end"]

@pytest.mark.asyncio
async def test_multiple_quick_triggers_only_rerun_once():
    calls = []

    async def task_fn():
        calls.append("run")
        await asyncio.sleep(0.01)

    trigger = FunctionTrigger(task_fn)

    first = asyncio.create_task(trigger.trigger_or_rerun())
    await asyncio.sleep(0.002)

    # These three should all coalesce into one rerun, not three more
    await asyncio.gather(
        trigger.trigger_or_rerun(),
        trigger.trigger_or_rerun(),
        trigger.trigger_or_rerun()
    )

    await first

    assert calls == ["run", "run"]