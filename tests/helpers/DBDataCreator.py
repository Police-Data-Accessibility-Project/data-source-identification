from typing import List, Optional

from pydantic import BaseModel

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInsertInfo
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo, HTMLContentType
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource, TaskType
from collector_manager.enums import CollectorType
from core.enums import BatchStatus
from tests.helpers.simple_test_data_functions import generate_test_urls


class BatchURLCreationInfo(BaseModel):
    batch_id: int
    url_ids: list[int]

class DBDataCreator:
    """
    Assists in the creation of test data
    """
    def __init__(self, db_client: DatabaseClient = DatabaseClient()):
        self.db_client = db_client
        self.adb_client: AsyncDatabaseClient = AsyncDatabaseClient()

    def batch(self, strategy: CollectorType = CollectorType.EXAMPLE) -> int:
        return self.db_client.insert_batch(
            BatchInfo(
                strategy=strategy.value,
                status=BatchStatus.IN_PROCESS,
                total_url_count=1,
                parameters={"test_key": "test_value"},
                user_id=1
            )
        )

    async def task(self, url_ids: Optional[list[int]] = None) -> int:
        task_id = await self.adb_client.initiate_task(task_type=TaskType.HTML)
        if url_ids is not None:
            await self.adb_client.link_urls_to_task(task_id=task_id, url_ids=url_ids)
        return task_id

    async def batch_and_urls(
            self,
            strategy: CollectorType = CollectorType.EXAMPLE,
            url_count: int = 1,
            with_html_content: bool = False
    ) -> BatchURLCreationInfo:
        batch_id = self.batch(strategy=strategy)
        iuis: InsertURLsInfo = self.urls(batch_id=batch_id, url_count=url_count)
        url_ids = [iui.url_id for iui in iuis.url_mappings]
        if with_html_content:
            await self.html_data(url_ids)

        return BatchURLCreationInfo(batch_id=batch_id, url_ids=url_ids)



    def urls(self, batch_id: int, url_count: int) -> InsertURLsInfo:
        raw_urls = generate_test_urls(url_count)
        url_infos: List[URLInfo] = []
        for url in raw_urls:
            url_infos.append(
                URLInfo(
                    url=url,
                )
            )

        return self.db_client.insert_urls(
            url_infos=url_infos,
            batch_id=batch_id,
        )

    def duplicate_urls(self, duplicate_batch_id: int, url_ids: list[int]):
        """
        Create duplicates for all given url ids, and associate them
        with the given batch
        """
        duplicate_infos = []
        for url_id in url_ids:
            dup_info = DuplicateInsertInfo(
                duplicate_batch_id=duplicate_batch_id,
                original_url_id=url_id
            )
            duplicate_infos.append(dup_info)

        self.db_client.insert_duplicates(duplicate_infos)

    async def html_data(self, url_ids: list[int]):
        html_content_infos = []
        for url_id in url_ids:
            html_content_infos.append(
                URLHTMLContentInfo(
                    url_id=url_id,
                    content_type=HTMLContentType.TITLE,
                    content="test html content"
                )
            )
            html_content_infos.append(
                URLHTMLContentInfo(
                    url_id=url_id,
                    content_type=HTMLContentType.DESCRIPTION,
                    content="test description"
                )
            )
        await self.adb_client.add_html_content_infos(html_content_infos)

    async def metadata(
            self,
            url_ids: list[int],
            attribute: URLMetadataAttributeType = URLMetadataAttributeType.RELEVANT,
            value: str = "False",
            validation_status: ValidationStatus = ValidationStatus.PENDING_VALIDATION,
            validation_source: ValidationSource = ValidationSource.MACHINE_LEARNING
    ):
        for url_id in url_ids:
            await self.adb_client.add_url_metadata(
                URLMetadataInfo(
                    url_id=url_id,
                    attribute=attribute,
                    value=value,
                    validation_status=validation_status,
                    validation_source=validation_source,
                )
            )

    async def error_info(
            self,
            url_ids: list[int],
            task_id: Optional[int] = None
    ):
        if task_id is None:
            task_id = await self.task()
        error_infos = []
        for url_id in url_ids:
            url_error_info = URLErrorPydanticInfo(
                url_id=url_id,
                error="test error",
                task_id=task_id
            )
            error_infos.append(url_error_info)
        await self.adb_client.add_url_error_infos(error_infos)

