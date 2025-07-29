from src.core.tasks.scheduled.huggingface.operator import PushToHuggingFaceTaskOperator
from tests.helpers.data_creator.core import DBDataCreator


async def test_happy_path(
    operator: PushToHuggingFaceTaskOperator,
    db_data_creator: DBDataCreator
):
    raise NotImplementedError

    # TODO: Check, prior to adding URLs, that task does not run


    # TODO: Add URLs


    # TODO: Run task


    # TODO: Check for calls to HF Client


    # TODO: Test that after update, running again yields no results