import pytest

from src.core.tasks.url.loader import URLTaskOperatorLoader

NUMBER_OF_TASK_OPERATORS = 9

@pytest.mark.asyncio
async def test_happy_path(
    loader: URLTaskOperatorLoader
):
    """
    Under normal circumstances, all task operators should be returned
    """
    task_operators = await loader.get_task_operators()
    assert len(task_operators) == NUMBER_OF_TASK_OPERATORS