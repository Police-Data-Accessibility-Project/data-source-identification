from unittest.mock import AsyncMock

import pytest

from src.collectors.impl.auto_googler.dtos.input import AutoGooglerInputDTO
from src.core.env_var_manager import EnvVarManager
from src.core.logger import AsyncCoreLogger
from src.collectors.impl.auto_googler.collector import AutoGooglerCollector
from src.db.client.async_ import AsyncDatabaseClient
from environs import Env

@pytest.mark.asyncio
async def test_autogoogler_collector(monkeypatch):
    env = Env()
    env.read_env()
    env_var_manager = EnvVarManager.get()
    env_var_manager.google_api_key = env("GOOGLE_API_KEY")
    env_var_manager.google_cse_id = env("GOOGLE_CSE_ID")

    collector = AutoGooglerCollector(
        batch_id=1,
        dto=AutoGooglerInputDTO(
            urls_per_result=20,
            queries=[
                "pennsylvania police officer roster"
            ],
        ),
        logger = AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run_to_completion()
    print(collector.data)