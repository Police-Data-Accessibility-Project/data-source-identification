import threading
import time
from unittest.mock import Mock, MagicMock

from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.enums import BatchStatus


# Mock a subclass to implement the abstract method
class MockCollector(CollectorBase):
    collector_type = CollectorType.EXAMPLE
    preprocessor = MagicMock()

    def __init__(self, dto, **kwargs):
        super().__init__(
            batch_id=1,
            dto=dto,
            logger=Mock(spec=CoreLogger),
            db_client=Mock(spec=DatabaseClient),
            raise_error=True
        )

    def run_implementation(self):
        while True:
            time.sleep(0.1)  # Simulate work
            self.log("Working...")

def test_collector_closes_properly():
    # Mock dependencies
    mock_dto = Mock()

    # Initialize the collector
    collector = MockCollector(
        dto=mock_dto,
    )

    # Run the collector in a separate thread
    thread = threading.Thread(target=collector.run)
    thread.start()

    # Run the collector for a time
    time.sleep(1)
    # Signal the collector to stop
    collector.abort()

    thread.join()



    # Assertions
    # Check that multiple log calls have been made
    assert collector.logger.log.call_count > 1
    # Check that last call to collector.logger.log was with the correct message
    assert collector.logger.log.call_args[0][0] == LogInfo(
        id=None,
        log='Collector was aborted.',
        batch_id=1,
        created_at=None
    )

    assert not thread.is_alive(), "Thread is still alive after aborting."
    assert collector._stop_event.is_set(), "Stop event was not set."
    assert collector.status == BatchStatus.ABORTED, "Collector status is not ABORTED."

    print("Test passed: Collector closes properly.")


