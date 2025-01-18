import threading
import time
from unittest.mock import MagicMock

from collector_db.DTOs.LogInfo import LogInfo
from core.CoreLogger import CoreLogger


def test_logger_flush():
    mock_db_client = MagicMock()
    logger = CoreLogger(flush_interval=1, db_client=mock_db_client)

    # Add logs
    logger.log(LogInfo(log="Log 1", batch_id=1))
    logger.log(LogInfo(log="Log 2", batch_id=1))

    # Wait for the flush interval
    time.sleep(1.5)

    # Verify logs were flushed
    assert mock_db_client.insert_logs.called
    flushed_logs = mock_db_client.insert_logs.call_args[1]['log_infos']
    assert len(flushed_logs) == 2
    assert flushed_logs[0].log == "Log 1"

    logger.shutdown()

def test_logger_multithreading():
    mock_db_client = MagicMock()
    logger = CoreLogger(flush_interval=1, db_client=mock_db_client, batch_size=10)

    def worker(thread_id):
        for i in range(5):  # Each thread logs 5 messages
            logger.log(LogInfo(log=f"Thread-{thread_id} Log-{i}", batch_id=thread_id))

    # Start multiple threads
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]  # 5 threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()  # Wait for all threads to finish

    # Allow the logger to flush
    time.sleep(2)
    logger.shutdown()

    # Verify all logs were flushed
    assert mock_db_client.insert_logs.called
    flushed_logs = []
    for call in mock_db_client.insert_logs.call_args_list:
        flushed_logs.extend(call[1]['log_infos'])

    # Ensure all logs are present
    assert len(flushed_logs) == 25  # 5 threads * 5 messages each
    for i in range(5):
        for j in range(5):
            assert any(log.log == f"Thread-{i} Log-{j}" for log in flushed_logs)


def test_logger_with_delays():
    mock_db_client = MagicMock()
    logger = CoreLogger(flush_interval=1, db_client=mock_db_client, batch_size=10)

    def worker(thread_id):
        for i in range(10):  # Each thread logs 10 messages
            logger.log(LogInfo(log=f"Thread-{thread_id} Log-{i}", batch_id=thread_id))
            time.sleep(0.1)  # Simulate delay between logs

    # Start multiple threads
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]  # 5 threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()  # Wait for all threads to finish

    # Allow the logger to flush
    time.sleep(2)
    logger.shutdown()

    # Verify that all logs are eventually flushed
    flushed_logs = []
    for call in mock_db_client.insert_logs.call_args_list:
        flushed_logs.extend(call[1]['log_infos'])

    assert len(flushed_logs) == 50  # 5 threads * 10 messages each

