from typing import Optional, Any


from collector_db.DatabaseClient import DatabaseClient
from core.enums import BatchStatus


class SourceCollectorCore:
    def __init__(
        self,
        db_client: Optional[DatabaseClient] = None,
    ):
        if db_client is None:
            db_client = DatabaseClient()
        self.db_client = db_client

    def get_status(self, batch_id: int) -> BatchStatus:
        return self.db_client.get_batch_status(batch_id)
