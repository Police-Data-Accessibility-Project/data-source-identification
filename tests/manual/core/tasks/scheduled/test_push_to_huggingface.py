import pytest

from environs import Env

from src.core.env_var_manager import EnvVarManager
from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.hub.client import HuggingFaceHubClient

env = Env()
env.read_env()

@pytest.mark.asyncio
@pytest.mark.manual
async def test_push_to_huggingface():
    operator = PushToHuggingFaceTaskOperator(
        adb_client=AsyncDatabaseClient(
            db_url=env.str("PROD_DATABASE_URL")
        ),
        hf_client=HuggingFaceHubClient(
            env.str("HUGGINGFACE_HUB_TOKEN")
        )
    )

    await operator.inner_task_logic()

