from datetime import datetime
from random import randint
from typing import List, Optional

from pydantic import BaseModel

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.enums import RejectionReason
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.batch.pydantic import BatchInfo
from src.db.models.instantiations.duplicate.pydantic.insert import DuplicateInsertInfo
from src.db.models.instantiations.url.suggestion.relevant.auto.pydantic.input import AutoRelevancyAnnotationInput
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.models.instantiations.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.dtos.url.html_content import URLHTMLContentInfo, HTMLContentType
from src.db.models.instantiations.url.core.pydantic import URLInfo
from src.db.dtos.url.mapping import URLMapping
from src.db.client.sync import DatabaseClient
from src.db.dtos.url.raw_html import RawHTMLInfo
from src.db.enums import TaskType
from src.collectors.enums import CollectorType, URLStatus
from src.core.tasks.url.operators.submit_approved_url.tdo import SubmittedURLInfo
from src.core.tasks.url.operators.url_miscellaneous_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.enums import BatchStatus, SuggestionType, RecordType, SuggestedStatus
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.simple_test_data_functions import generate_test_urls


class URLCreationInfo(BaseModel):
    url_mappings: list[URLMapping]
    outcome: URLStatus
    annotation_info: Optional[AnnotationInfo] = None

    @property
    def url_ids(self) -> list[int]:
        return [url_mapping.url_id for url_mapping in self.url_mappings]

class BatchURLCreationInfoV2(BaseModel):
    batch_id: int
    url_creation_infos: dict[URLStatus, URLCreationInfo]

    @property
    def url_ids(self) -> list[int]:
        url_creation_infos = self.url_creation_infos.values()
        url_ids = []
        for url_creation_info in url_creation_infos:
            url_ids.extend(url_creation_info.url_ids)
        return url_ids

class BatchURLCreationInfo(BaseModel):
    batch_id: int
    url_ids: list[int]
    urls: list[str]

class DBDataCreator:
    """
    Assists in the creation of test data
    """
    def __init__(self, db_client: Optional[DatabaseClient] = None):
        if db_client is not None:
            self.db_client = db_client
        else:
            self.db_client = DatabaseClient()
        self.adb_client: AsyncDatabaseClient = AsyncDatabaseClient()

    def batch(
        self,
        strategy: CollectorType = CollectorType.EXAMPLE,
        batch_status: BatchStatus = BatchStatus.IN_PROCESS,
        created_at: Optional[datetime] = None
    ) -> int:
        return self.db_client.insert_batch(
            BatchInfo(
                strategy=strategy.value,
                status=batch_status,
                parameters={"test_key": "test_value"},
                user_id=1,
                date_generated=created_at
            )
        )

    async def task(self, url_ids: Optional[list[int]] = None) -> int:
        task_id = await self.adb_client.initiate_task(task_type=TaskType.HTML)
        if url_ids is not None:
            await self.adb_client.link_urls_to_task(task_id=task_id, url_ids=url_ids)
        return task_id

    async def batch_v2(
        self,
        parameters: TestBatchCreationParameters
    ) -> BatchURLCreationInfoV2:
        batch_id = self.batch(
            strategy=parameters.strategy,
            batch_status=parameters.outcome,
            created_at=parameters.created_at
        )
        if parameters.outcome in (BatchStatus.ERROR, BatchStatus.ABORTED):
            return BatchURLCreationInfoV2(
                batch_id=batch_id,
                url_creation_infos={}
            )

        d: dict[URLStatus, URLCreationInfo] = {}
        # Create urls
        for url_parameters in parameters.urls:
            iui: InsertURLsInfo = self.urls(
                batch_id=batch_id,
                url_count=url_parameters.count,
                outcome=url_parameters.status,
                created_at=parameters.created_at
            )
            url_ids = [iui.url_id for iui in iui.url_mappings]
            if url_parameters.with_html_content:
                await self.html_data(url_ids)
            if url_parameters.annotation_info.has_annotations():
                for url_id in url_ids:
                    await self.annotate(
                        url_id=url_id,
                        annotation_info=url_parameters.annotation_info
                    )

            d[url_parameters.status] = URLCreationInfo(
                url_mappings=iui.url_mappings,
                outcome=url_parameters.status,
                annotation_info=url_parameters.annotation_info if url_parameters.annotation_info.has_annotations() else None
            )
        return BatchURLCreationInfoV2(
            batch_id=batch_id,
            url_creation_infos=d
        )

    async def batch_and_urls(
            self,
            strategy: CollectorType = CollectorType.EXAMPLE,
            url_count: int = 3,
            with_html_content: bool = False,
            batch_status: BatchStatus = BatchStatus.READY_TO_LABEL,
            url_status: URLStatus = URLStatus.PENDING
    ) -> BatchURLCreationInfo:
        batch_id = self.batch(
            strategy=strategy,
            batch_status=batch_status
        )
        if batch_status in (BatchStatus.ERROR, BatchStatus.ABORTED):
            return BatchURLCreationInfo(
                batch_id=batch_id,
                url_ids=[],
                urls=[]
            )
        iuis: InsertURLsInfo = self.urls(
            batch_id=batch_id,
            url_count=url_count,
            outcome=url_status
        )
        url_ids = [iui.url_id for iui in iuis.url_mappings]
        if with_html_content:
            await self.html_data(url_ids)

        return BatchURLCreationInfo(
            batch_id=batch_id,
            url_ids=url_ids,
            urls=[iui.url for iui in iuis.url_mappings]
        )

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

    async def auto_relevant_suggestions(self, url_id: int, relevant: bool = True):
        await self.adb_client.add_auto_relevant_suggestion(
            input_=AutoRelevancyAnnotationInput(
                url_id=url_id,
                is_relevant=relevant,
                confidence=0.5,
                model_name="test_model"
            )
        )

    async def annotate(
        self,
        url_id: int,
        annotation_info: AnnotationInfo
    ):
        info = annotation_info
        if info.user_relevant is not None:
            await self.user_relevant_suggestion_v2(url_id=url_id, suggested_status=info.user_relevant)
        if info.auto_relevant is not None:
            await self.auto_relevant_suggestions(url_id=url_id, relevant=info.auto_relevant)
        if info.user_record_type is not None:
            await self.user_record_type_suggestion(url_id=url_id, record_type=info.user_record_type)
        if info.auto_record_type is not None:
            await self.auto_record_type_suggestions(url_id=url_id, record_type=info.auto_record_type)
        if info.user_agency is not None:
            await self.agency_user_suggestions(url_id=url_id, agency_annotation_info=info.user_agency)
        if info.auto_agency is not None:
            await self.agency_auto_suggestions(url_id=url_id, count=1, suggestion_type=SuggestionType.AUTO_SUGGESTION)
        if info.confirmed_agency is not None:
            await self.agency_auto_suggestions(url_id=url_id, count=1, suggestion_type=SuggestionType.CONFIRMED)
        if info.final_review_approved is not None:
            if info.final_review_approved:
                final_review_approval_info = FinalReviewApprovalInfo(
                    url_id=url_id,
                    record_type=annotation_info.user_record_type,
                    agency_ids=[annotation_info.user_agency.suggested_agency]
                    if annotation_info.user_agency is not None else None,
                    description="Test Description",
                )
                await self.adb_client.approve_url(
                    approval_info=final_review_approval_info,
                    user_id=1
                )
            else:
                await self.adb_client.reject_url(
                    url_id=url_id,
                    user_id=1,
                    rejection_reason=RejectionReason.NOT_RELEVANT
                )


    async def user_relevant_suggestion(
            self,
            url_id: int,
            user_id: Optional[int] = None,
            relevant: bool = True
    ):
        await self.user_relevant_suggestion_v2(
            url_id=url_id,
            user_id=user_id,
            suggested_status=SuggestedStatus.RELEVANT if relevant else SuggestedStatus.NOT_RELEVANT
        )

    async def user_relevant_suggestion_v2(
            self,
            url_id: int,
            user_id: Optional[int] = None,
            suggested_status: SuggestedStatus = SuggestedStatus.RELEVANT
    ):
        if user_id is None:
            user_id = randint(1, 99999999)
        await self.adb_client.add_user_relevant_suggestion(
            url_id=url_id,
            user_id=user_id,
            suggested_status=suggested_status
        )

    async def user_record_type_suggestion(
            self,
            url_id: int,
            record_type: RecordType,
            user_id: Optional[int] = None,
    ):
        if user_id is None:
            user_id = randint(1, 99999999)
        await self.adb_client.add_user_record_type_suggestion(
            url_id=url_id,
            user_id=user_id,
            record_type=record_type
        )

    async def auto_record_type_suggestions(self, url_id: int, record_type: RecordType):
        await self.adb_client.add_auto_record_type_suggestion(
            url_id=url_id,
            record_type=record_type
        )


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


    def urls(
            self,
            batch_id: int,
            url_count: int,
            collector_metadata: Optional[dict] = None,
            outcome: URLStatus = URLStatus.PENDING,
            created_at: Optional[datetime] = None
    ) -> InsertURLsInfo:
        raw_urls = generate_test_urls(url_count)
        url_infos: List[URLInfo] = []
        for url in raw_urls:
            url_infos.append(
                URLInfo(
                    url=url,
                    outcome=outcome,
                    name="Test Name" if outcome == URLStatus.VALIDATED else None,
                    collector_metadata=collector_metadata,
                    created_at=created_at
                )
            )

        url_insert_info = self.db_client.insert_urls(
            url_infos=url_infos,
            batch_id=batch_id,
        )

        # If outcome is submitted, also add entry to DataSourceURL
        if outcome == URLStatus.SUBMITTED:
            submitted_url_infos = []
            for url_id in url_insert_info.url_ids:
                submitted_url_info = SubmittedURLInfo(
                    url_id=url_id,
                    data_source_id=url_id, # Use same ID for convenience,
                    request_error=None,
                    submitted_at=created_at
                )
                submitted_url_infos.append(submitted_url_info)
            self.db_client.mark_urls_as_submitted(submitted_url_infos)


        return url_insert_info

    async def url_miscellaneous_metadata(
            self,
            url_id: int,
            name: str = "Test Name",
            description: str = "Test Description",
            record_formats: Optional[list[str]] = None,
            data_portal_type: Optional[str] = "Test Data Portal Type",
            supplying_entity: Optional[str] = "Test Supplying Entity"
    ):
        if record_formats is None:
            record_formats = ["Test Record Format", "Test Record Format 2"]

        tdo = URLMiscellaneousMetadataTDO(
            url_id=url_id,
            collector_metadata={},
            collector_type=CollectorType.EXAMPLE,
            record_formats=record_formats,
            name=name,
            description=description,
            data_portal_type=data_portal_type,
            supplying_entity=supplying_entity
        )

        await self.adb_client.add_miscellaneous_metadata([tdo])


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
        raw_html_info_list = []
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
            raw_html_info = RawHTMLInfo(
                url_id=url_id,
                html="<html></html>"
            )
            raw_html_info_list.append(raw_html_info)

        await self.adb_client.add_raw_html(raw_html_info_list)
        await self.adb_client.add_html_content_infos(html_content_infos)

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


    async def agency_auto_suggestions(
            self,
            url_id: int,
            count: int,
            suggestion_type: SuggestionType = SuggestionType.AUTO_SUGGESTION
    ):
        if suggestion_type == SuggestionType.UNKNOWN:
            count = 1  # Can only be one auto suggestion if unknown

        suggestions = []
        for _ in range(count):
            if suggestion_type == SuggestionType.UNKNOWN:
                pdap_agency_id = None
            else:
                pdap_agency_id = await self.agency()
            suggestion = URLAgencySuggestionInfo(
                    url_id=url_id,
                    suggestion_type=suggestion_type,
                    pdap_agency_id=pdap_agency_id,
                    state="Test State",
                    county="Test County",
                    locality="Test Locality"
            )
            suggestions.append(suggestion)

        await self.adb_client.add_agency_auto_suggestions(
            suggestions=suggestions
        )

    async def agency_confirmed_suggestion(
            self,
            url_id: int
    ) -> int:
        """
        Creates a confirmed agency suggestion
        and returns the auto-generated pdap_agency_id
        """
        agency_id = await self.agency()
        await self.adb_client.add_confirmed_agency_url_links(
            suggestions=[
                URLAgencySuggestionInfo(
                    url_id=url_id,
                    suggestion_type=SuggestionType.CONFIRMED,
                    pdap_agency_id=agency_id
                )
            ]
        )
        return agency_id

    async def agency_user_suggestions(
            self,
            url_id: int,
            user_id: Optional[int] = None,
            agency_annotation_info: Optional[URLAgencyAnnotationPostInfo] = None
    ):
        if user_id is None:
            user_id = randint(1, 99999999)

        if agency_annotation_info is None:
            agency_annotation_info = URLAgencyAnnotationPostInfo(
                suggested_agency=await self.agency()
            )
        await self.adb_client.add_agency_manual_suggestion(
            agency_id=agency_annotation_info.suggested_agency,
            url_id=url_id,
            user_id=user_id,
            is_new=agency_annotation_info.is_new
        )
