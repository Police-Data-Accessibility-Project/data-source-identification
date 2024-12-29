import threading
import time
from unittest.mock import Mock

from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from core.enums import BatchStatus


# Mock a subclass to implement the abstract method
class MockCollector(CollectorBase):
    collector_type = CollectorType.EXAMPLE

    def run_implementation(self):
        while not self._stop_event.is_set():
            time.sleep(0.1)  # Simulate work

def test_collector_closes_properly():
    # Mock dependencies
    mock_logger = Mock()
    mock_dto = Mock()

    # Initialize the collector
    collector = MockCollector(batch_id=1, dto=mock_dto, logger=mock_logger)

    # Run the collector in a separate thread
    thread = threading.Thread(target=collector.run)
    thread.start()

    # Let the thread start
    time.sleep(0.2)

    # Signal the collector to stop
    close_info = collector.abort()

    # Wait for the thread to finish
    thread.join()

    # Assertions
    assert not thread.is_alive(), "Thread is still alive after aborting."
    assert collector._stop_event.is_set(), "Stop event was not set."
    assert close_info.status == BatchStatus.ABORTED, "Collector status is not ABORTED."
    assert close_info.message == "Collector aborted.", "Unexpected close message."

    print("Test passed: Collector closes properly.")

# Run the test
test_collector_closes_properly()
