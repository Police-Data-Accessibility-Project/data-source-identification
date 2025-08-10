import pytest

from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader

NUMBER_OF_ENTRIES = 6

@pytest.mark.asyncio
async def test_happy_path(
    loader: ScheduledTaskOperatorLoader
):
    """
    Under normal circumstances, all task operators should be returned
    """
    entries = await loader.load_entries()
    assert len(entries) == NUMBER_OF_ENTRIES