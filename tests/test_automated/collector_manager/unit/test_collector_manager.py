import threading
import time
from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from collector_manager.CollectorManager import CollectorManager, InvalidCollectorError
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.CoreLogger import CoreLogger
from core.enums import BatchStatus


@dataclass
class ExampleCollectorSetup:
    type = CollectorType.EXAMPLE
    dto = ExampleInputDTO(
        example_field="example_value", sleep_time=1
    )
    manager = CollectorManager(
        logger=Mock(spec=CoreLogger)
    )

    def start_collector(self, batch_id: int):
        self.manager.start_collector(self.type, batch_id, self.dto)


@pytest.fixture
def ecs():
    ecs = ExampleCollectorSetup()
    yield ecs
    ecs.manager.shutdown_all_collectors()



def test_start_collector(ecs: ExampleCollectorSetup):
    manager = ecs.manager

    batch_id = 1
    ecs.start_collector(batch_id)
    assert batch_id in manager.collectors, "Collector not added to manager."
    thread = manager.threads.get(batch_id)
    assert thread is not None, "Thread not started for collector."
    assert thread.is_alive(), "Thread is not running."

    print("Test passed: Collector starts correctly.")

def test_abort_collector(ecs: ExampleCollectorSetup):
    batch_id = 2
    manager = ecs.manager

    ecs.start_collector(batch_id)

    close_info = manager.close_collector(batch_id)

    assert batch_id not in manager.collectors, "Collector not removed after closure."
    assert batch_id not in manager.threads, "Thread not removed after closure."
    assert close_info.status == BatchStatus.ABORTED, "Collector status not ABORTED."

    print("Test passed: Collector aborts properly.")


def test_invalid_collector(ecs: ExampleCollectorSetup):
    invalid_batch_id = 999

    try:
        ecs.manager.close_collector(invalid_batch_id)
    except InvalidCollectorError as e:
        assert str(e) == f"Collector with CID {invalid_batch_id} not found."
        print("Test passed: Invalid collector error handled correctly.")
    else:
        assert False, "No error raised for invalid collector."

def test_concurrent_collectors(ecs: ExampleCollectorSetup):
    manager = ecs.manager

    batch_ids = [1, 2, 3]

    threads = []
    for batch_id in batch_ids:
        thread = threading.Thread(target=manager.start_collector, args=(ecs.type, batch_id, ecs.dto))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert all(batch_id in manager.collectors for batch_id in batch_ids), "Not all collectors started."
    assert all(manager.threads[batch_id].is_alive() for batch_id in batch_ids), "Not all threads are running."

    print("Test passed: Concurrent collectors managed correctly.")

def test_thread_safety(ecs: ExampleCollectorSetup):
    import concurrent.futures

    manager = ecs.manager

    def start_and_close(batch_id):
        ecs.start_collector(batch_id)
        time.sleep(0.1)  # Simulate some processing
        manager.close_collector(batch_id)

    batch_ids = [i for i in range(1, 6)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(start_and_close, batch_ids)

    assert not manager.collectors, "Some collectors were not cleaned up."
    assert not manager.threads, "Some threads were not cleaned up."

    print("Test passed: Thread safety maintained under concurrent access.")

def test_shutdown_all_collectors(ecs: ExampleCollectorSetup):
    manager = ecs.manager

    batch_ids = [1, 2, 3]

    for batch_id in batch_ids:
        ecs.start_collector(batch_id)

    manager.shutdown_all_collectors()

    assert not manager.collectors, "Not all collectors were removed."
    assert not manager.threads, "Not all threads were cleaned up."

    print("Test passed: Shutdown cleans up all collectors and threads.")
