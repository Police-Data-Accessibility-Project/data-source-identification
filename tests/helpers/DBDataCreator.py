from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DatabaseClient import DatabaseClient
from core.enums import BatchStatus


class DBDataCreator:
    """
    Assists in the creation of test data
    """
    def __init__(self, db_client: DatabaseClient = DatabaseClient()):
        self.db_client = db_client

    def batch(self):
        return self.db_client.insert_batch(
            BatchInfo(
                strategy="test_batch",
                status=BatchStatus.IN_PROCESS,
                total_url_count=1,
                parameters={"test_key": "test_value"}
            )
        )
