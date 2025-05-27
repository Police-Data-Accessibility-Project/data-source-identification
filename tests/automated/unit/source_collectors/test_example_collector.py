from unittest.mock import AsyncMock

from src.db.DatabaseClient import DatabaseClient
from src.collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from src.collector_manager.ExampleCollector import ExampleCollector
from src.core.AsyncCoreLogger import AsyncCoreLogger


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