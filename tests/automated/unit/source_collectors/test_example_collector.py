from unittest.mock import AsyncMock

from db.DatabaseClient import DatabaseClient
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.ExampleCollector import ExampleCollector
from core.AsyncCoreLogger import AsyncCoreLogger


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