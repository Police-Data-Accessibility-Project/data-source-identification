from typing import List

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DatabaseClient import DatabaseClient
from core.enums import BatchStatus
from helpers.simple_test_data_functions import generate_test_urls


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
                parameters={"test_key": "test_value"},
                user_id=1
            )
        )

    def urls(self, batch_id: int, url_count: int) -> InsertURLsInfo:
        raw_urls = generate_test_urls(url_count)
        url_infos: List[URLInfo] = []
        for url in raw_urls:
            url_infos.append(
                URLInfo(
                    url=url,
                )
            )

        return self.db_client.insert_urls(url_infos=url_infos, batch_id=batch_id)
