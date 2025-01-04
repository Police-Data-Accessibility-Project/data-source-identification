from unittest.mock import MagicMock

from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from source_collectors.auto_googler.AutoGooglerCollector import AutoGooglerCollector
from source_collectors.auto_googler.DTOs import AutoGooglerInputDTO


def test_autogoogler_collector():
    collector = AutoGooglerCollector(
        batch_id=1,
        dto=AutoGooglerInputDTO(
            urls_per_result=5,
            queries=["police"],
        ),
        logger = MagicMock(spec=CoreLogger),
        db_client=MagicMock(spec=DatabaseClient),
        raise_error=True
    )
    collector.run()
    print(collector.data)