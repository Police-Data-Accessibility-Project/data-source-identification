from unittest.mock import AsyncMock

from src.db.client.sync import DatabaseClient
from src.collectors.source_collectors.example.dtos.input import ExampleInputDTO
from src.collectors.source_collectors.example.core import ExampleCollector
from src.core.logger import AsyncCoreLogger


def test_example_collector():
    collector = ExampleCollector(
        batch_id=1,
        dto=ExampleInputDTO(
            sleep_time=1
        ),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=DatabaseClient),
        raise_error=True
    )
    collector.run()