import threading
import time

from collector_db.DTOs.LogInfo import LogInfo
from core.CoreLogger import CoreLogger
from tests.helpers.DBDataCreator import DBDataCreator


def test_logger_integration(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    db_client = db_data_creator.db_client
    with CoreLogger(flush_interval=1, db_client=db_client) as logger:

        # Simulate logging
        logger.log(LogInfo(log="Integration Log 1", batch_id=batch_id))
        logger.log(LogInfo(log="Integration Log 2", batch_id=batch_id))

        # Wait for the flush interval
        time.sleep(1.5)

        # Verify logs in the database
        logs = db_client.get_logs_by_batch_id(batch_id)
        assert len(logs) == 2
        assert logs[0].log == "Integration Log 1"


def test_multithreaded_integration_with_live_db(db_data_creator: DBDataCreator):
    # Ensure the database is empty
    db_client = db_data_creator.db_client
    db_client.delete_all_logs()

    batch_ids = [db_data_creator.batch() for _ in range(5)]
    db_client = db_data_creator.db_client
    logger = CoreLogger(flush_interval=1, db_client=db_client, batch_size=10)

    # Simulate multiple threads logging
    def worker(thread_id):
        batch_id = batch_ids[thread_id-1]
        for i in range(10):  # Each thread logs 10 messages
            logger.log(LogInfo(log=f"Thread-{thread_id} Log-{i}", batch_id=batch_id))

    # Start multiple threads
    threads = [threading.Thread(target=worker, args=(i+1,)) for i in range(5)]  # 5 threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Allow the logger to flush
    logger.shutdown()
    time.sleep(10)

    # Verify logs in the database
    logs = db_client.get_all_logs()

    # Optional: Print logs for manual inspection
    for log in logs:
        print(log.log)

    # Assertions
    assert len(logs) == 50  # 5 threads * 10 messages each
    for i in range(1,6):
        for j in range(10):
            assert any(log.log == f"Thread-{i} Log-{j}" for log in logs)


