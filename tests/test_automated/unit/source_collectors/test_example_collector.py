from unittest.mock import MagicMock

from collector_db.DatabaseClient import DatabaseClient
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.ExampleCollector import ExampleCollector
from core.CoreLogger import CoreLogger


def test_example_collector():
    collector = ExampleCollector(
        batch_id=1,
        dto=ExampleInputDTO(
            sleep_time=1
        ),
        logger=MagicMock(spec=CoreLogger),
        db_client=MagicMock(spec=DatabaseClient),
        raise_error=True
    )
    collector.run()