from random import randint
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
from core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from core.enums import BatchStatus, SuggestionType
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

    async def agency(self) -> int:
        agency_id = randint(1, 99999999)
        await self.adb_client.upsert_new_agencies(
            suggestions=[
                URLAgencySuggestionInfo(
                    url_id=-1,
                    suggestion_type=SuggestionType.UNKNOWN,
                    pdap_agency_id=agency_id,
                    agency_name=f"Test Agency {agency_id}",
                    state=f"Test State {agency_id}",
                    county=f"Test County {agency_id}",
                    locality=f"Test Locality {agency_id}"
                )
            ]
        )
        return agency_id

    async def auto_suggestions(
            self,
            url_ids: list[int],
            num_suggestions: int,
            suggestion_type: SuggestionType.AUTO_SUGGESTION or SuggestionType.UNKNOWN
    ):
        allowed_suggestion_types = [SuggestionType.AUTO_SUGGESTION, SuggestionType.UNKNOWN]
        if suggestion_type not in allowed_suggestion_types:
            raise ValueError(f"suggestion_type must be one of {allowed_suggestion_types}")
        if suggestion_type == SuggestionType.UNKNOWN and num_suggestions > 1:
            raise ValueError("num_suggestions must be 1 when suggestion_type is unknown")

        for url_id in url_ids:
            suggestions = []
            for i in range(num_suggestions):
                if suggestion_type == SuggestionType.UNKNOWN:
                    agency_id = None
                else:
                    agency_id = await self.agency()
                suggestion = URLAgencySuggestionInfo(
                    url_id=url_id,
                    suggestion_type=suggestion_type,
                    pdap_agency_id=agency_id
                )
                suggestions.append(suggestion)

            await self.adb_client.add_agency_auto_suggestions(
                suggestions=suggestions
            )

    async def confirmed_suggestions(self, url_ids: list[int]):
        for url_id in url_ids:
            await self.adb_client.add_confirmed_agency_url_links(
                suggestions=[
                    URLAgencySuggestionInfo(
                        url_id=url_id,
                        suggestion_type=SuggestionType.CONFIRMED,
                        pdap_agency_id=await self.agency()
                    )
                ]
            )

    async def manual_suggestion(self, user_id: int, url_id: int, is_new: bool = False):
        await self.adb_client.add_agency_manual_suggestion(
            agency_id=await self.agency(),
            url_id=url_id,
            user_id=user_id,
            is_new=is_new
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
    ) -> list[int]:
        metadata_ids = []
        for url_id in url_ids:
            metadata_id = await self.adb_client.add_url_metadata(
                URLMetadataInfo(
                    url_id=url_id,
                    attribute=attribute,
                    value=value,
                    validation_status=validation_status,
                    validation_source=validation_source,
                )
            )
            metadata_ids.append(metadata_id)
        return metadata_ids

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

    async def user_annotation(
            self,
            metadata_id: int,
            user_id: Optional[int] = None,
            annotation: str = "test annotation"
    ):
        if user_id is None:
            user_id = randint(1, 99999999)
        await self.adb_client.add_metadata_annotation(
            user_id=user_id,
            metadata_id=metadata_id,
            annotation=annotation
        )

    async def agency_auto_suggestions(
            self,
            url_id: int,
            count: int,
            suggestion_type: SuggestionType = SuggestionType.AUTO_SUGGESTION
    ):
        if suggestion_type == SuggestionType.UNKNOWN:
            count = 1  # Can only be one auto suggestion if unknown

        await self.adb_client.add_agency_auto_suggestions(
            suggestions=[
                URLAgencySuggestionInfo(
                    url_id=url_id,
                    suggestion_type=suggestion_type,
                    pdap_agency_id=None if suggestion_type == SuggestionType.UNKNOWN else await self.agency(),
                    state="Test State",
                    county="Test County",
                    locality="Test Locality"
                ) for _ in range(count)
            ]
        )

    async def agency_confirmed_suggestion(
            self,
            url_id: int
    ):

        await self.adb_client.add_confirmed_agency_url_links(
            suggestions=[
                URLAgencySuggestionInfo(
                    url_id=url_id,
                    suggestion_type=SuggestionType.CONFIRMED,
                    pdap_agency_id=await self.agency()
                )
            ]
        )

    async def agency_user_suggestions(
            self,
            url_id: int,
            user_id: Optional[int] = None,
            agency_id: Optional[int] = None
    ):
        if user_id is None:
            user_id = randint(1, 99999999)

        if agency_id is None:
            agency_id = await self.agency()
        await self.adb_client.add_agency_manual_suggestion(
            agency_id=agency_id,
            url_id=url_id,
            user_id=user_id,
            is_new=False
        )
