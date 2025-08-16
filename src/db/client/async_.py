from datetime import datetime, timedelta
from functools import wraps
from operator import or_
from typing import Optional, Type, Any, List, Sequence

from sqlalchemy import select, exists, func, case, Select, and_, update, delete, literal, Row
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, QueryableAttribute

from src.api.endpoints.annotate._shared.queries.get_annotation_batch_info import GetAnnotationBatchInfoQueryBuilder
from src.api.endpoints.annotate._shared.queries.get_next_url_for_user_annotation import \
    GetNextURLForUserAnnotationQueryBuilder
from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAnnotationResponse
from src.api.endpoints.annotate.agency.get.queries.next_for_annotation import GetNextURLAgencyForAnnotationQueryBuilder
from src.api.endpoints.annotate.all.get.dto import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.get.query import GetNextURLForAllAnnotationQueryBuilder
from src.api.endpoints.annotate.all.post.dto import AllAnnotationPostInfo
from src.api.endpoints.annotate.dtos.record_type.response import GetNextRecordTypeAnnotationResponseInfo
from src.api.endpoints.annotate.relevance.get.dto import GetNextRelevanceAnnotationResponseInfo
from src.api.endpoints.annotate.relevance.get.query import GetNextUrlForRelevanceAnnotationQueryBuilder
from src.api.endpoints.batch.dtos.get.summaries.response import GetBatchSummariesResponse
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.api.endpoints.batch.duplicates.query import GetDuplicatesByBatchIDQueryBuilder
from src.api.endpoints.batch.urls.query import GetURLsByBatchQueryBuilder
from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.api.endpoints.collector.manual.query import UploadManualBatchQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.dto import GetMetricsBatchesAggregatedResponseDTO
from src.api.endpoints.metrics.batches.aggregated.query import GetBatchesAggregatedMetricsQueryBuilder
from src.api.endpoints.metrics.batches.breakdown.dto import GetMetricsBatchesBreakdownResponseDTO
from src.api.endpoints.metrics.batches.breakdown.query import GetBatchesBreakdownMetricsQueryBuilder
from src.api.endpoints.metrics.dtos.get.backlog import GetMetricsBacklogResponseDTO, GetMetricsBacklogResponseInnerDTO
from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLsAggregatedResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.pending import GetMetricsURLsBreakdownPendingResponseDTO, \
    GetMetricsURLsBreakdownPendingResponseInnerDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.submitted import GetMetricsURLsBreakdownSubmittedResponseDTO, \
    GetMetricsURLsBreakdownSubmittedInnerDTO
from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.approve.query_.core import ApproveURLQueryBuilder
from src.api.endpoints.review.enums import RejectionReason
from src.api.endpoints.review.next.dto import GetNextURLForFinalReviewOuterResponse
from src.api.endpoints.review.next.query import GetNextURLForFinalReviewQueryBuilder
from src.api.endpoints.review.reject.query import RejectURLQueryBuilder
from src.api.endpoints.search.dtos.response import SearchURLResponse
from src.api.endpoints.task.by_id.dto import TaskInfo
from src.api.endpoints.task.by_id.query import GetTaskInfoQueryBuilder
from src.api.endpoints.task.dtos.get.tasks import GetTasksResponse, GetTasksResponseTaskInfo
from src.api.endpoints.url.get.dto import GetURLsResponseInfo
from src.api.endpoints.url.get.query import GetURLsQueryBuilder
from src.collectors.enums import URLStatus, CollectorType
from src.collectors.queries.insert.urls.query import InsertURLsQueryBuilder
from src.core.enums import BatchStatus, SuggestionType, RecordType, SuggestedStatus
from src.core.env_var_manager import EnvVarManager
from src.core.tasks.scheduled.impl.huggingface.queries.check.core import CheckValidURLsUpdatedQueryBuilder
from src.core.tasks.scheduled.impl.huggingface.queries.get.core import GetForLoadingToHuggingFaceQueryBuilder
from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from src.core.tasks.scheduled.impl.huggingface.queries.state import SetHuggingFaceUploadStateQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.dtos.parameters import AgencySyncParameters
from src.core.tasks.scheduled.impl.sync.agency.queries.get_sync_params import GetAgenciesSyncParametersQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.mark_full_sync import get_mark_full_agencies_sync_query
from src.core.tasks.scheduled.impl.sync.agency.queries.update_sync_progress import \
    get_update_agencies_sync_progress_query
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert import \
    convert_agencies_sync_response_to_agencies_upsert
from src.core.tasks.scheduled.impl.sync.data_sources.params import DataSourcesSyncParameters
from src.core.tasks.scheduled.impl.sync.data_sources.queries.get_sync_params import \
    GetDataSourcesSyncParametersQueryBuilder
from src.core.tasks.scheduled.impl.sync.data_sources.queries.mark_full_sync import get_mark_full_data_sources_sync_query
from src.core.tasks.scheduled.impl.sync.data_sources.queries.update_sync_progress import \
    get_update_data_sources_sync_progress_query
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.core import \
    UpsertURLsFromDataSourcesQueryBuilder
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.dtos.tdo import AgencyIdentificationTDO
from src.core.tasks.url.operators.agency_identification.queries.get_pending_urls_without_agency_suggestions import \
    GetPendingURLsWithoutAgencySuggestionsQueryBuilder
from src.core.tasks.url.operators.agency_identification.queries.has_urls_without_agency_suggestions import \
    HasURLsWithoutAgencySuggestionsQueryBuilder
from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO
from src.core.tasks.url.operators.auto_relevant.queries.get_tdos import GetAutoRelevantTDOsQueryBuilder
from src.core.tasks.url.operators.html.queries.get import \
    GetPendingURLsWithoutHTMLDataQueryBuilder
from src.core.tasks.url.operators.misc_metadata.queries.get_pending_urls_missing_miscellaneous_data import \
    GetPendingURLsMissingMiscellaneousDataQueryBuilder
from src.core.tasks.url.operators.misc_metadata.queries.has_pending_urls_missing_miscellaneous_data import \
    HasPendingURsMissingMiscellaneousDataQueryBuilder
from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.tasks.url.operators.probe.queries.urls.not_probed.exists import HasURLsWithoutProbeQueryBuilder
from src.core.tasks.url.operators.probe.queries.urls.not_probed.get.query import GetURLsWithoutProbeQueryBuilder
from src.core.tasks.url.operators.probe_404.tdo import URL404ProbeTDO
from src.core.tasks.url.operators.submit_approved.queries.get import GetValidatedURLsQueryBuilder
from src.core.tasks.url.operators.submit_approved.queries.has_validated import HasValidatedURLsQueryBuilder
from src.core.tasks.url.operators.submit_approved.queries.mark_submitted import MarkURLsAsSubmittedQueryBuilder
from src.core.tasks.url.operators.submit_approved.tdo import SubmitApprovedURLTDO, SubmittedURLInfo
from src.db.client.helpers import add_standard_limit_and_offset
from src.db.client.types import UserSuggestionModel
from src.db.config_manager import ConfigManager
from src.db.constants import PLACEHOLDER_AGENCY_NAME
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.dtos.url.mapping import URLMapping
from src.db.dtos.url.raw_html import RawHTMLInfo
from src.db.enums import TaskType
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.backlog_snapshot import BacklogSnapshot
from src.db.models.impl.batch.pydantic import BatchInfo
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.duplicate.pydantic.info import DuplicateInfo
from src.db.models.impl.link.task_url import LinkTaskURL
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.log.pydantic.info import LogInfo
from src.db.models.impl.log.pydantic.output import LogOutputInfo
from src.db.models.impl.log.sqlalchemy import Log
from src.db.models.impl.task.core import Task
from src.db.models.impl.task.error import TaskError
from src.db.models.impl.url.checked_for_duplicate import URLCheckedForDuplicate
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.models.impl.url.error_info.sqlalchemy import URLErrorInfo
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.models.impl.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.impl.url.probed_for_404 import URLProbedFor404
from src.db.models.impl.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.auto.pydantic.input import AutoRelevancyAnnotationInput
from src.db.models.impl.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.models.templates_.base import Base
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.core.get.html_content_info import GetHTMLContentInfoQueryBuilder
from src.db.queries.implementations.core.get.recent_batch_summaries.builder import GetRecentBatchSummariesQueryBuilder
from src.db.queries.implementations.core.metrics.urls.aggregated.pending import \
    GetMetricsURLSAggregatedPendingQueryBuilder
from src.db.statement_composer import StatementComposer
from src.db.templates.markers.bulk.delete import BulkDeletableModel
from src.db.templates.markers.bulk.insert import BulkInsertableModel
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel
from src.db.utils.compression import decompress_html, compress_html
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo


class AsyncDatabaseClient:
    def __init__(self, db_url: str | None = None):
        if db_url is None:
            db_url = EnvVarManager.get().get_postgres_connection_string(is_async=True)
        self.db_url = db_url
        echo = ConfigManager.get_sqlalchemy_echo()
        self.engine = create_async_engine(
            url=db_url,
            echo=echo,
        )
        self.session_maker = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        self.statement_composer = StatementComposer()

    @staticmethod
    async def _add_models(session: AsyncSession, model_class, models) -> list[int]:
        instances = [model_class(**model.model_dump()) for model in models]
        session.add_all(instances)
        await session.flush()
        return [instance.id for instance in instances]

    @staticmethod
    def session_manager(method):
        """Decorator to manage async session lifecycle."""

        @wraps(method)
        async def wrapper(self, *args, **kwargs):
            async with self.session_maker() as session:
                async with session.begin():
                    try:
                        result = await method(self, session, *args, **kwargs)
                        return result
                    except Exception as e:
                        await session.rollback()
                        raise e

        return wrapper

    @session_manager
    async def execute(self, session: AsyncSession, statement):
        await session.execute(statement)

    @session_manager
    async def add(
        self,
        session: AsyncSession,
        model: Base,
        return_id: bool = False
    ) -> int | None:
        return await sh.add(session=session, model=model, return_id=return_id)

    @session_manager
    async def add_all(
        self,
        session: AsyncSession,
        models: list[Base],
        return_ids: bool = False
    ) -> list[int] | None:
        return await sh.add_all(session=session, models=models, return_ids=return_ids)

    @session_manager
    async def bulk_update(
        self,
        session: AsyncSession,
        model: Base,
        mappings: list[dict],
    ):
        # Note, mapping must include primary key
        await session.execute(
            update(model),
            mappings
        )

    @session_manager
    async def bulk_upsert(
        self,
        session: AsyncSession,
        models: list[BulkUpsertableModel],
    ):
        return await sh.bulk_upsert(session, models)

    @session_manager
    async def bulk_delete(
        self,
        session: AsyncSession,
        models: list[BulkDeletableModel],
    ):
        return await sh.bulk_delete(session, models)

    @session_manager
    async def bulk_insert(
        self,
        session: AsyncSession,
        models: list[BulkInsertableModel],
        return_ids: bool = False
    ) -> list[int] | None:
        return await sh.bulk_insert(session, models=models, return_ids=return_ids)

    @session_manager
    async def scalar(self, session: AsyncSession, statement):
        """Fetch the first column of the first row."""
        return await sh.scalar(session, statement)

    @session_manager
    async def scalars(self, session: AsyncSession, statement):
        return await sh.scalars(session, statement)

    @session_manager
    async def mapping(self, session: AsyncSession, statement):
        return await sh.mapping(session, statement)

    @session_manager
    async def one_or_none(self, session: AsyncSession, statement):
        return await sh.one_or_none(session, statement)

    @session_manager
    async def run_query_builder(
        self,
        session: AsyncSession,
        builder: QueryBuilderBase
    ) -> Any:
        return await builder.run(session=session)

    # region relevant
    async def add_auto_relevant_suggestion(
        self,
        input_: AutoRelevancyAnnotationInput
    ):
        await self.add_user_relevant_suggestions(inputs=[input_])

    async def add_user_relevant_suggestions(
        self,
        inputs: list[AutoRelevancyAnnotationInput]
    ):
        models = [
            AutoRelevantSuggestion(
                url_id=input_.url_id,
                relevant=input_.is_relevant,
                confidence=input_.confidence,
                model_name=input_.model_name
            )
            for input_ in inputs
        ]
        await self.add_all(models)

    @staticmethod
    async def get_user_suggestion(
        session: AsyncSession,
        model: UserSuggestionModel,
        user_id: int,
        url_id: int
    ) -> UserSuggestionModel | None:
        statement = Select(model).where(
            and_(
                model.url_id == url_id,
                model.user_id == user_id
            )
        )
        result = await session.execute(statement)
        return result.unique().scalar_one_or_none()

    async def get_next_url_for_user_annotation(
        self,
        user_suggestion_model_to_exclude: UserSuggestionModel,
        auto_suggestion_relationship: QueryableAttribute,
        batch_id: int | None,
        check_if_annotated_not_relevant: bool = False
    ) -> URL:
        return await self.run_query_builder(
            builder=GetNextURLForUserAnnotationQueryBuilder(
                user_suggestion_model_to_exclude=user_suggestion_model_to_exclude,
                auto_suggestion_relationship=auto_suggestion_relationship,
                batch_id=batch_id,
                check_if_annotated_not_relevant=check_if_annotated_not_relevant
            )
        )

    async def get_tdos_for_auto_relevancy(self) -> list[URLRelevantTDO]:
        return await self.run_query_builder(builder=GetAutoRelevantTDOsQueryBuilder())

    @session_manager
    async def add_user_relevant_suggestion(
        self,
        session: AsyncSession,
        url_id: int,
        user_id: int,
        suggested_status: SuggestedStatus
    ):
        prior_suggestion = await self.get_user_suggestion(
            session,
            model=UserRelevantSuggestion,
            user_id=user_id,
            url_id=url_id
        )
        if prior_suggestion is not None:
            prior_suggestion.suggested_status = suggested_status.value
            return

        suggestion = UserRelevantSuggestion(
            url_id=url_id,
            user_id=user_id,
            suggested_status=suggested_status.value
        )
        session.add(suggestion)

    async def get_next_url_for_relevance_annotation(
        self,
        batch_id: int | None,
        user_id: int | None = None,
    ) -> GetNextRelevanceAnnotationResponseInfo | None:
        return await self.run_query_builder(GetNextUrlForRelevanceAnnotationQueryBuilder(batch_id))

    # endregion relevant

    # region record_type

    @session_manager
    async def get_next_url_for_record_type_annotation(
        self,
        session: AsyncSession,
        user_id: int,
        batch_id: int | None
    ) -> GetNextRecordTypeAnnotationResponseInfo | None:

        url = await GetNextURLForUserAnnotationQueryBuilder(
            user_suggestion_model_to_exclude=UserRecordTypeSuggestion,
            auto_suggestion_relationship=URL.auto_record_type_suggestion,
            batch_id=batch_id,
            check_if_annotated_not_relevant=True
        ).run(session)
        if url is None:
            return None

        # Next, get all HTML content for the URL
        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        if url.auto_record_type_suggestion is not None:
            suggestion = url.auto_record_type_suggestion.record_type
        else:
            suggestion = None

        return GetNextRecordTypeAnnotationResponseInfo(
            url_info=URLMapping(
                url=url.url,
                url_id=url.id
            ),
            suggested_record_type=suggestion,
            html_info=html_response_info,
            batch_info=await GetAnnotationBatchInfoQueryBuilder(
                batch_id=batch_id,
                models=[
                    UserUrlAgencySuggestion,
                ]
            ).run(session)
        )

    @session_manager
    async def add_auto_record_type_suggestions(
        self,
        session: AsyncSession,
        url_and_record_type_list: list[tuple[int, RecordType]]
    ):
        for url_id, record_type in url_and_record_type_list:
            suggestion = AutoRecordTypeSuggestion(
                url_id=url_id,
                record_type=record_type.value
            )
            session.add(suggestion)

    async def add_auto_record_type_suggestion(
        self,
        url_id: int,
        record_type: RecordType
    ):
        suggestion = AutoRecordTypeSuggestion(
            url_id=url_id,
            record_type=record_type.value
        )
        await self.add(suggestion)

    @session_manager
    async def add_user_record_type_suggestion(
        self,
        session: AsyncSession,
        url_id: int,
        user_id: int,
        record_type: RecordType
    ):
        prior_suggestion = await self.get_user_suggestion(
            session,
            model=UserRecordTypeSuggestion,
            user_id=user_id,
            url_id=url_id
        )
        if prior_suggestion is not None:
            prior_suggestion.record_type = record_type.value
            return

        suggestion = UserRecordTypeSuggestion(
            url_id=url_id,
            user_id=user_id,
            record_type=record_type.value
        )
        session.add(suggestion)

    # endregion record_type

    @session_manager
    async def add_url_error_infos(self, session: AsyncSession, url_error_infos: list[URLErrorPydanticInfo]):
        for url_error_info in url_error_infos:
            statement = select(URL).where(URL.id == url_error_info.url_id)
            scalar_result = await session.scalars(statement)
            url = scalar_result.first()
            url.status = URLStatus.ERROR.value

            url_error = URLErrorInfo(**url_error_info.model_dump())
            session.add(url_error)

    @session_manager
    async def get_urls_with_errors(self, session: AsyncSession) -> list[URLErrorPydanticInfo]:
        statement = (select(URL, URLErrorInfo.error, URLErrorInfo.updated_at, URLErrorInfo.task_id)
                     .join(URLErrorInfo)
                     .where(URL.status == URLStatus.ERROR.value)
                     .order_by(URL.id))
        scalar_result = await session.execute(statement)
        results = scalar_result.all()
        final_results = []
        for url, error, updated_at, task_id in results:
            final_results.append(
                URLErrorPydanticInfo(
                    url_id=url.id,
                    error=error,
                    updated_at=updated_at,
                    task_id=task_id
                )
            )

        return final_results

    @session_manager
    async def add_html_content_infos(self, session: AsyncSession, html_content_infos: list[URLHTMLContentInfo]):
        await self._add_models(session, URLHTMLContent, html_content_infos)

    @session_manager
    async def has_non_errored_urls_without_html_data(self, session: AsyncSession) -> bool:
        statement = self.statement_composer.has_non_errored_urls_without_html_data()
        statement = statement.limit(1)
        scalar_result = await session.scalars(statement)
        return bool(scalar_result.first())

    async def has_pending_urls_missing_miscellaneous_metadata(self) -> bool:
        return await self.run_query_builder(HasPendingURsMissingMiscellaneousDataQueryBuilder())

    async def get_pending_urls_missing_miscellaneous_metadata(
        self,
    ) -> list[URLMiscellaneousMetadataTDO]:
        return await self.run_query_builder(GetPendingURLsMissingMiscellaneousDataQueryBuilder())

    @session_manager
    async def add_miscellaneous_metadata(self, session: AsyncSession, tdos: list[URLMiscellaneousMetadataTDO]):
        updates = []

        for tdo in tdos:
            update_query = update(
                URL
            ).where(
                URL.id == tdo.url_id
            ).values(
                name=tdo.name,
                description=tdo.description,
            )

            updates.append(update_query)

        for stmt in updates:
            await session.execute(stmt)

        for tdo in tdos:
            metadata_object = URLOptionalDataSourceMetadata(
                url_id=tdo.url_id,
                record_formats=tdo.record_formats,
                data_portal_type=tdo.data_portal_type,
                supplying_entity=tdo.supplying_entity
            )
            session.add(metadata_object)

    async def get_non_errored_urls_without_html_data(self) -> list[URLInfo]:
        return await self.run_query_builder(GetPendingURLsWithoutHTMLDataQueryBuilder())

    async def get_urls_with_html_data_and_without_models(
        self,
        session: AsyncSession,
        model: Type[Base]
    ):
        statement = (select(URL)
                     .options(selectinload(URL.html_content))
                     .where(URL.status == URLStatus.PENDING.value))
        statement = self.statement_composer.exclude_urls_with_extant_model(
            statement=statement,
            model=model
        )
        statement = statement.limit(100).order_by(URL.id)
        raw_result = await session.execute(statement)
        urls: Sequence[Row[URL]] = raw_result.unique().scalars().all()
        final_results = DTOConverter.url_list_to_url_with_html_list(urls)

        return final_results

    @session_manager
    async def get_urls_with_html_data_and_without_auto_record_type_suggestion(
        self,
        session: AsyncSession
    ):
        return await self.get_urls_with_html_data_and_without_models(
            session=session,
            model=AutoRecordTypeSuggestion
        )

    async def has_urls_with_html_data_and_without_models(
        self,
        session: AsyncSession,
        model: Type[Base]
    ) -> bool:
        statement = (select(URL)
                     .join(URLCompressedHTML)
                     .where(URL.status == URLStatus.PENDING.value))
        # Exclude URLs with auto suggested record types
        statement = self.statement_composer.exclude_urls_with_extant_model(
            statement=statement,
            model=model
        )
        statement = statement.limit(1)
        scalar_result = await session.scalars(statement)
        return bool(scalar_result.first())

    @session_manager
    async def has_urls_with_html_data_and_without_auto_relevant_suggestion(self, session: AsyncSession) -> bool:
        return await self.has_urls_with_html_data_and_without_models(
            session=session,
            model=AutoRelevantSuggestion
        )

    @session_manager
    async def has_urls_with_html_data_and_without_auto_record_type_suggestion(self, session: AsyncSession) -> bool:
        return await self.has_urls_with_html_data_and_without_models(
            session=session,
            model=AutoRecordTypeSuggestion
        )

    @session_manager
    async def get_all(
        self,
        session,
        model: Base,
        order_by_attribute: str | None = None
    ) -> list[Base]:
        """Get all records of a model. Used primarily in testing."""
        return await sh.get_all(session=session, model=model, order_by_attribute=order_by_attribute)

    async def get_urls(
        self,
        page: int,
        errors: bool
    ) -> GetURLsResponseInfo:
        return await self.run_query_builder(GetURLsQueryBuilder(
            page=page, errors=errors
        ))

    @session_manager
    async def initiate_task(
        self,
        session: AsyncSession,
        task_type: TaskType
    ) -> int:
        # Create Task
        task = Task(
            task_type=task_type,
            task_status=BatchStatus.IN_PROCESS.value
        )
        session.add(task)
        # Return Task ID
        await session.flush()
        await session.refresh(task)
        return task.id

    @session_manager
    async def update_task_status(self, session: AsyncSession, task_id: int, status: BatchStatus):
        task = await session.get(Task, task_id)
        task.task_status = status.value

    async def add_task_error(self, task_id: int, error: str):
        task_error = TaskError(
            task_id=task_id,
            error=error
        )
        await self.add(task_error)

    async def get_task_info(
        self,
        task_id: int
    ) -> TaskInfo:
        return await self.run_query_builder(GetTaskInfoQueryBuilder(task_id))

    async def get_html_content_info(self, url_id: int) -> list[URLHTMLContentInfo]:
        return await self.run_query_builder(GetHTMLContentInfoQueryBuilder(url_id))

    @session_manager
    async def link_urls_to_task(self, session: AsyncSession, task_id: int, url_ids: list[int]):
        for url_id in url_ids:
            link = LinkTaskURL(
                url_id=url_id,
                task_id=task_id
            )
            session.add(link)

    @session_manager
    async def get_tasks(
        self,
        session: AsyncSession,
        task_type: Optional[TaskType] = None,
        task_status: Optional[BatchStatus] = None,
        page: int = 1
    ) -> GetTasksResponse:
        url_count_subquery = self.statement_composer.simple_count_subquery(
            LinkTaskURL,
            'task_id',
            'url_count'
        )

        url_error_count_subquery = self.statement_composer.simple_count_subquery(
            URLErrorInfo,
            'task_id',
            'url_error_count'
        )

        statement = select(
            Task,
            url_count_subquery.c.url_count,
            url_error_count_subquery.c.url_error_count
        ).outerjoin(
            url_count_subquery,
            Task.id == url_count_subquery.c.task_id
        ).outerjoin(
            url_error_count_subquery,
            Task.id == url_error_count_subquery.c.task_id
        )
        if task_type is not None:
            statement = statement.where(Task.task_type == task_type.value)
        if task_status is not None:
            statement = statement.where(Task.task_status == task_status.value)
        add_standard_limit_and_offset(statement, page)

        execute_result = await session.execute(statement)
        all_results = execute_result.all()
        final_results = []
        for task, url_count, url_error_count in all_results:
            final_results.append(
                GetTasksResponseTaskInfo(
                    task_id=task.id,
                    type=TaskType(task.task_type),
                    status=BatchStatus(task.task_status),
                    url_count=url_count if url_count is not None else 0,
                    url_error_count=url_error_count if url_error_count is not None else 0,
                    updated_at=task.updated_at
                )
            )
        return GetTasksResponse(
            tasks=final_results
        )

    async def has_urls_without_agency_suggestions(self) -> bool:
        return await self.run_query_builder(HasURLsWithoutAgencySuggestionsQueryBuilder())

    async def get_urls_without_agency_suggestions(
        self
    ) -> list[AgencyIdentificationTDO]:
        """Retrieve URLs without confirmed or suggested agencies."""
        return await self.run_query_builder(GetPendingURLsWithoutAgencySuggestionsQueryBuilder())

    async def get_next_url_agency_for_annotation(
        self,
        user_id: int,
        batch_id: int | None
    ) -> GetNextURLForAgencyAnnotationResponse:
        return await self.run_query_builder(builder=GetNextURLAgencyForAnnotationQueryBuilder(
            user_id=user_id,
            batch_id=batch_id
        ))

    @session_manager
    async def upsert_new_agencies(
        self,
        session: AsyncSession,
        suggestions: list[URLAgencySuggestionInfo]
    ):
        """
        Add or update agencies in the database
        """
        for suggestion in suggestions:
            query = select(Agency).where(Agency.agency_id == suggestion.pdap_agency_id)
            result = await session.execute(query)
            agency = result.scalars().one_or_none()
            if agency is None:
                agency = Agency(agency_id=suggestion.pdap_agency_id)
            agency.name = suggestion.agency_name
            agency.state = suggestion.state
            agency.county = suggestion.county
            agency.locality = suggestion.locality
            session.add(agency)

    @session_manager
    async def add_confirmed_agency_url_links(
        self,
        session: AsyncSession,
        suggestions: list[URLAgencySuggestionInfo]
    ):
        for suggestion in suggestions:
            confirmed_agency = LinkURLAgency(
                url_id=suggestion.url_id,
                agency_id=suggestion.pdap_agency_id
            )
            session.add(confirmed_agency)

    @session_manager
    async def add_agency_auto_suggestions(
        self,
        session: AsyncSession,
        suggestions: list[URLAgencySuggestionInfo]
    ):
        for suggestion in suggestions:
            url_agency_suggestion = AutomatedUrlAgencySuggestion(
                url_id=suggestion.url_id,
                agency_id=suggestion.pdap_agency_id,
                is_unknown=suggestion.suggestion_type == SuggestionType.UNKNOWN
            )
            session.add(url_agency_suggestion)

    @session_manager
    async def add_agency_manual_suggestion(
        self,
        session: AsyncSession,
        agency_id: Optional[int],
        url_id: int,
        user_id: int,
        is_new: bool
    ):
        if is_new and agency_id is not None:
            raise ValueError("agency_id must be None when is_new is True")

        # Check if agency exists in database -- if not, add with placeholder
        if agency_id is not None:
            statement = select(Agency).where(Agency.agency_id == agency_id)
            result = await session.execute(statement)
            if len(result.all()) == 0:
                agency = Agency(
                    agency_id=agency_id,
                    name=PLACEHOLDER_AGENCY_NAME
                )
                await session.merge(agency)

        url_agency_suggestion = UserUrlAgencySuggestion(
            url_id=url_id,
            agency_id=agency_id,
            user_id=user_id,
            is_new=is_new
        )
        session.add(url_agency_suggestion)

    @session_manager
    async def get_urls_with_confirmed_agencies(self, session: AsyncSession) -> list[URL]:
        statement = select(URL).where(exists().where(LinkURLAgency.url_id == URL.id))
        results = await session.execute(statement)
        return list(results.scalars().all())

    @session_manager
    async def get_next_url_for_final_review(
        self,
        session: AsyncSession,
        batch_id: Optional[int]
    ) -> GetNextURLForFinalReviewOuterResponse:

        builder = GetNextURLForFinalReviewQueryBuilder(
            batch_id=batch_id
        )
        result = await builder.run(session)
        return result

    async def approve_url(
        self,
        approval_info: FinalReviewApprovalInfo,
        user_id: int,
    ) -> None:
        await self.run_query_builder(ApproveURLQueryBuilder(
            user_id=user_id,
            approval_info=approval_info
        ))

    async def reject_url(
        self,
        url_id: int,
        user_id: int,
        rejection_reason: RejectionReason
    ) -> None:
        await self.run_query_builder(RejectURLQueryBuilder(
            url_id=url_id,
            user_id=user_id,
            rejection_reason=rejection_reason
        ))

    @session_manager
    async def get_batch_by_id(self, session, batch_id: int) -> Optional[BatchSummary]:
        """Retrieve a batch by ID."""
        builder = GetRecentBatchSummariesQueryBuilder(
            batch_id=batch_id
        )
        summaries = await builder.run(session)
        if len(summaries) == 0:
            return None
        batch_summary = summaries[0]
        return batch_summary

    async def get_urls_by_batch(self, batch_id: int, page: int = 1) -> list[URLInfo]:
        """Retrieve all URLs associated with a batch."""
        return await self.run_query_builder(GetURLsByBatchQueryBuilder(
            batch_id=batch_id,
            page=page
        ))

    @session_manager
    async def insert_logs(
        self,
        session: AsyncSession,
        log_infos: list[LogInfo]
    ) -> None:
        for log_info in log_infos:
            log = Log(log=log_info.log, batch_id=log_info.batch_id)
            if log_info.created_at is not None:
                log.created_at = log_info.created_at
            session.add(log)

    @session_manager
    async def insert_batch(
        self,
        session: AsyncSession,
        batch_info: BatchInfo
    ) -> int:
        """Insert a new batch into the database and return its ID."""
        batch = Batch(
            strategy=batch_info.strategy,
            user_id=batch_info.user_id,
            status=batch_info.status.value,
            parameters=batch_info.parameters,
            compute_time=batch_info.compute_time,
            strategy_success_rate=0,
            metadata_success_rate=0,
            agency_match_rate=0,
            record_type_match_rate=0,
            record_category_match_rate=0,
        )
        if batch_info.date_generated is not None:
            batch.date_generated = batch_info.date_generated
        session.add(batch)
        await session.flush()
        return batch.id

    async def insert_urls(
        self,
        url_infos: list[URLInfo],
        batch_id: int
    ) -> InsertURLsInfo:
        builder = InsertURLsQueryBuilder(
            url_infos=url_infos,
            batch_id=batch_id
        )
        return await self.run_query_builder(builder)



    @session_manager
    async def update_batch_post_collection(
        self,
        session: AsyncSession,
        batch_id: int,
        total_url_count: int,
        original_url_count: int,
        duplicate_url_count: int,
        batch_status: BatchStatus,
        compute_time: float = None,
    ) -> None:

        query = Select(Batch).where(Batch.id == batch_id)
        result = await session.execute(query)
        batch = result.scalars().first()

        batch.total_url_count = total_url_count
        batch.original_url_count = original_url_count
        batch.duplicate_url_count = duplicate_url_count
        batch.status = batch_status.value
        batch.compute_time = compute_time

    async def has_validated_urls(self) -> bool:
        return await self.run_query_builder(HasValidatedURLsQueryBuilder())

    async def get_validated_urls(self) -> list[SubmitApprovedURLTDO]:
        return await self.run_query_builder(GetValidatedURLsQueryBuilder())

    async def mark_urls_as_submitted(self, infos: list[SubmittedURLInfo]):
        await self.run_query_builder(MarkURLsAsSubmittedQueryBuilder(infos))

    async def get_duplicates_by_batch_id(self, batch_id: int, page: int) -> list[DuplicateInfo]:
        return await self.run_query_builder(GetDuplicatesByBatchIDQueryBuilder(
            batch_id=batch_id,
            page=page
        ))

    @session_manager
    async def get_batch_summaries(
        self,
        session,
        page: int,
        collector_type: Optional[CollectorType] = None,
        status: Optional[BatchStatus] = None,
        has_pending_urls: Optional[bool] = None
    ) -> GetBatchSummariesResponse:
        # Get only the batch_id, collector_type, status, and created_at
        builder = GetRecentBatchSummariesQueryBuilder(
            page=page,
            collector_type=collector_type,
            status=status,
            has_pending_urls=has_pending_urls
        )
        summaries = await builder.run(session)
        return GetBatchSummariesResponse(
            results=summaries
        )

    @session_manager
    async def get_logs_by_batch_id(self, session, batch_id: int) -> List[LogOutputInfo]:
        query = Select(Log).filter_by(batch_id=batch_id).order_by(Log.created_at.asc())
        raw_results = await session.execute(query)
        logs = raw_results.scalars().all()
        return ([LogOutputInfo(**log.__dict__) for log in logs])

    async def delete_old_logs(self):
        """
        Delete logs older than a day
        """
        statement = delete(Log).where(
            Log.created_at < datetime.now() - timedelta(days=7)
        )
        await self.execute(statement)

    async def get_next_url_for_all_annotations(
        self, batch_id: int | None = None
    ) -> GetNextURLForAllAnnotationResponse:
        return await self.run_query_builder(GetNextURLForAllAnnotationQueryBuilder(batch_id))

    @session_manager
    async def add_all_annotations_to_url(
        self,
        session,
        user_id: int,
        url_id: int,
        post_info: AllAnnotationPostInfo
    ):

        # Add relevant annotation
        relevant_suggestion = UserRelevantSuggestion(
            url_id=url_id,
            user_id=user_id,
            suggested_status=post_info.suggested_status.value
        )
        session.add(relevant_suggestion)

        # If not relevant, do nothing else
        if not post_info.suggested_status == SuggestedStatus.RELEVANT:
            return

        record_type_suggestion = UserRecordTypeSuggestion(
            url_id=url_id,
            user_id=user_id,
            record_type=post_info.record_type.value
        )
        session.add(record_type_suggestion)

        agency_suggestion = UserUrlAgencySuggestion(
            url_id=url_id,
            user_id=user_id,
            agency_id=post_info.agency.suggested_agency,
            is_new=post_info.agency.is_new
        )
        session.add(agency_suggestion)

    async def upload_manual_batch(
        self,
        user_id: int,
        dto: ManualBatchInputDTO
    ) -> ManualBatchResponseDTO:
        return await self.run_query_builder(UploadManualBatchQueryBuilder(
            user_id=user_id,
            dto=dto
        ))

    @session_manager
    async def search_for_url(self, session: AsyncSession, url: str) -> SearchURLResponse:
        query = select(URL).where(URL.url == url)
        raw_results = await session.execute(query)
        url = raw_results.scalars().one_or_none()
        if url is None:
            return SearchURLResponse(
                found=False,
                url_id=None
            )
        return SearchURLResponse(
            found=True,
            url_id=url.id
        )

    async def get_batches_aggregated_metrics(self) -> GetMetricsBatchesAggregatedResponseDTO:
        return await self.run_query_builder(
            GetBatchesAggregatedMetricsQueryBuilder()
        )

    async def get_batches_breakdown_metrics(
        self,
        page: int
    ) -> GetMetricsBatchesBreakdownResponseDTO:
        return await self.run_query_builder(
            GetBatchesBreakdownMetricsQueryBuilder(
                page=page
            )
        )

    @session_manager
    async def get_urls_breakdown_submitted_metrics(
        self,
        session: AsyncSession
    ) -> GetMetricsURLsBreakdownSubmittedResponseDTO:

        # Build the query
        month = func.date_trunc('month', URLDataSource.created_at)
        query = (
            select(
                month.label('month'),
                func.count(URLDataSource.id).label('count_submitted'),
            )
            .group_by(month)
            .order_by(month.asc())
        )

        # Execute the query
        raw_results = await session.execute(query)
        results = raw_results.all()
        final_results: list[GetMetricsURLsBreakdownSubmittedInnerDTO] = []
        for result in results:
            dto = GetMetricsURLsBreakdownSubmittedInnerDTO(
                month=result.month.strftime("%B %Y"),
                count_submitted=result.count_submitted
            )
            final_results.append(dto)
        return GetMetricsURLsBreakdownSubmittedResponseDTO(
            entries=final_results
        )

    @session_manager
    async def get_urls_aggregated_metrics(
        self,
        session: AsyncSession
    ) -> GetMetricsURLsAggregatedResponseDTO:
        sc = StatementComposer

        oldest_pending_url_query = select(
            URL.id,
            URL.created_at
        ).where(
            URL.status == URLStatus.PENDING.value
        ).order_by(
            URL.created_at.asc()
        ).limit(1)

        oldest_pending_url = await session.execute(oldest_pending_url_query)
        oldest_pending_url = oldest_pending_url.one_or_none()
        if oldest_pending_url is None:
            oldest_pending_url_id = None
            oldest_pending_created_at = None
        else:
            oldest_pending_url_id = oldest_pending_url.id
            oldest_pending_created_at = oldest_pending_url.created_at

        def case_column(status: URLStatus, label):
            return sc.count_distinct(
                case(
                    (
                        URL.status == status.value,
                        URL.id
                    )
                ),
                label=label
            )

        count_query = select(
            sc.count_distinct(URL.id, label="count"),
            case_column(URLStatus.PENDING, label="count_pending"),
            case_column(URLStatus.SUBMITTED, label="count_submitted"),
            case_column(URLStatus.VALIDATED, label="count_validated"),
            case_column(URLStatus.NOT_RELEVANT, label="count_rejected"),
            case_column(URLStatus.ERROR, label="count_error"),
        )
        raw_results = await session.execute(count_query)
        results = raw_results.all()

        return GetMetricsURLsAggregatedResponseDTO(
            count_urls_total=results[0].count,
            count_urls_pending=results[0].count_pending,
            count_urls_submitted=results[0].count_submitted,
            count_urls_validated=results[0].count_validated,
            count_urls_rejected=results[0].count_rejected,
            count_urls_errors=results[0].count_error,
            oldest_pending_url_id=oldest_pending_url_id,
            oldest_pending_url_created_at=oldest_pending_created_at,
        )

    @session_manager
    async def get_urls_breakdown_pending_metrics(
        self,
        session: AsyncSession
    ) -> GetMetricsURLsBreakdownPendingResponseDTO:
        sc = StatementComposer

        flags = (
            select(
                URL.id.label("url_id"),
                case((UserRecordTypeSuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_record_type_annotation"
                ),
                case((UserRelevantSuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_relevant_annotation"
                ),
                case((UserUrlAgencySuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_agency_annotation"
                ),
            )
            .outerjoin(UserRecordTypeSuggestion, URL.id == UserRecordTypeSuggestion.url_id)
            .outerjoin(UserRelevantSuggestion, URL.id == UserRelevantSuggestion.url_id)
            .outerjoin(UserUrlAgencySuggestion, URL.id == UserUrlAgencySuggestion.url_id)
        ).cte("flags")

        month = func.date_trunc('month', URL.created_at)

        # Build the query
        query = (
            select(
                month.label('month'),
                func.count(URL.id).label('count_total'),
                func.count(
                    case(
                        (flags.c.has_user_record_type_annotation == True, 1)
                    )
                ).label('user_record_type_count'),
                func.count(
                    case(
                        (flags.c.has_user_relevant_annotation == True, 1)
                    )
                ).label('user_relevant_count'),
                func.count(
                    case(
                        (flags.c.has_user_agency_annotation == True, 1)
                    )
                ).label('user_agency_count'),
            )
            .outerjoin(flags, flags.c.url_id == URL.id)
            .where(URL.status == URLStatus.PENDING.value)
            .group_by(month)
            .order_by(month.asc())
        )

        # Execute the query and return the results
        results = await session.execute(query)
        all_results = results.all()
        final_results: list[GetMetricsURLsBreakdownPendingResponseInnerDTO] = []

        for result in all_results:
            dto = GetMetricsURLsBreakdownPendingResponseInnerDTO(
                month=result.month.strftime("%B %Y"),
                count_pending_total=result.count_total,
                count_pending_relevant_user=result.user_relevant_count,
                count_pending_record_type_user=result.user_record_type_count,
                count_pending_agency_user=result.user_agency_count,
            )
            final_results.append(dto)
        return GetMetricsURLsBreakdownPendingResponseDTO(
            entries=final_results,
        )

    @session_manager
    async def get_backlog_metrics(
        self,
        session: AsyncSession
    ) -> GetMetricsBacklogResponseDTO:
        month = func.date_trunc('month', BacklogSnapshot.created_at)

        # 1. Create a subquery that assigns row_number() partitioned by month
        monthly_snapshot_subq = (
            select(
                BacklogSnapshot.id,
                BacklogSnapshot.created_at,
                BacklogSnapshot.count_pending_total,
                month.label("month_start"),
                func.row_number()
                .over(
                    partition_by=month,
                    order_by=BacklogSnapshot.created_at.desc()
                )
                .label("row_number")
            )
            .subquery()
        )

        # 2. Filter for the top (most recent) row in each month
        stmt = (
            select(
                monthly_snapshot_subq.c.month_start,
                monthly_snapshot_subq.c.created_at,
                monthly_snapshot_subq.c.count_pending_total
            )
            .where(monthly_snapshot_subq.c.row_number == 1)
            .order_by(monthly_snapshot_subq.c.month_start)
        )

        raw_result = await session.execute(stmt)
        results = raw_result.all()
        final_results = []
        for result in results:
            final_results.append(
                GetMetricsBacklogResponseInnerDTO(
                    month=result.month_start.strftime("%B %Y"),
                    count_pending_total=result.count_pending_total,
                )
            )

        return GetMetricsBacklogResponseDTO(entries=final_results)

    @session_manager
    async def populate_backlog_snapshot(
        self,
        session: AsyncSession,
        dt: Optional[datetime] = None
    ):
        sc = StatementComposer
        # Get count of pending URLs
        query = select(
            sc.count_distinct(URL.id, label="count")
        ).where(
            URL.status == URLStatus.PENDING.value
        )

        raw_result = await session.execute(query)
        count = raw_result.one()[0]

        # insert count into snapshot
        snapshot = BacklogSnapshot(
            count_pending_total=count
        )
        if dt is not None:
            snapshot.created_at = dt

        session.add(snapshot)

    async def mark_all_as_404(self, url_ids: List[int]):
        query = update(URL).where(URL.id.in_(url_ids)).values(status=URLStatus.NOT_FOUND.value)
        await self.execute(query)
        query = update(URLWebMetadata).where(URLWebMetadata.url_id.in_(url_ids)).values(status_code=404)
        await self.execute(query)

    async def mark_all_as_recently_probed_for_404(
        self,
        url_ids: List[int],
        dt: datetime = func.now()
    ):
        values = [
            {"url_id": url_id, "last_probed_at": dt} for url_id in url_ids
        ]
        stmt = pg_insert(URLProbedFor404).values(values)
        update_stmt = stmt.on_conflict_do_update(
            index_elements=['url_id'],
            set_={"last_probed_at": dt}
        )
        await self.execute(update_stmt)

    @session_manager
    async def mark_as_checked_for_duplicates(self, session: AsyncSession, url_ids: list[int]):
        for url_id in url_ids:
            url_checked_for_duplicate = URLCheckedForDuplicate(url_id=url_id)
            session.add(url_checked_for_duplicate)

    @session_manager
    async def has_pending_urls_not_recently_probed_for_404(self, session: AsyncSession) -> bool:
        month_ago = func.now() - timedelta(days=30)
        query = (
            select(
                URL.id
            ).outerjoin(
                URLProbedFor404
            ).where(
                and_(
                    URL.status == URLStatus.PENDING.value,
                    or_(
                        URLProbedFor404.id == None,
                        URLProbedFor404.last_probed_at < month_ago
                    )
                )
            ).limit(1)
        )

        raw_result = await session.execute(query)
        result = raw_result.one_or_none()
        return result is not None

    @session_manager
    async def get_pending_urls_not_recently_probed_for_404(self, session: AsyncSession) -> List[URL404ProbeTDO]:
        month_ago = func.now() - timedelta(days=30)
        query = (
            select(
                URL
            ).outerjoin(
                URLProbedFor404
            ).where(
                and_(
                    URL.status == URLStatus.PENDING.value,
                    or_(
                        URLProbedFor404.id == None,
                        URLProbedFor404.last_probed_at < month_ago
                    )
                )
            ).limit(100)
        )

        raw_result = await session.execute(query)
        urls = raw_result.scalars().all()
        return [URL404ProbeTDO(url=url.url, url_id=url.id) for url in urls]

    async def get_urls_aggregated_pending_metrics(self):
        return await self.run_query_builder(GetMetricsURLSAggregatedPendingQueryBuilder())

    async def get_agencies_sync_parameters(self) -> AgencySyncParameters:
        return await self.run_query_builder(
            GetAgenciesSyncParametersQueryBuilder()
        )

    async def get_data_sources_sync_parameters(self) -> DataSourcesSyncParameters:
        return await self.run_query_builder(
            GetDataSourcesSyncParametersQueryBuilder()
        )

    async def upsert_agencies(
        self,
        agencies: list[AgenciesSyncResponseInnerInfo]
    ) -> None:
        await self.bulk_upsert(
            models=convert_agencies_sync_response_to_agencies_upsert(agencies)
        )

    async def upsert_urls_from_data_sources(
        self,
        data_sources: list[DataSourcesSyncResponseInnerInfo]
    ) -> None:
        await self.run_query_builder(
            UpsertURLsFromDataSourcesQueryBuilder(
                sync_infos=data_sources
            )
        )

    async def update_agencies_sync_progress(self, page: int) -> None:
        await self.execute(get_update_agencies_sync_progress_query(page))

    async def update_data_sources_sync_progress(self, page: int) -> None:
        await self.execute(get_update_data_sources_sync_progress_query(page))

    async def mark_full_data_sources_sync(self) -> None:
        await self.execute(get_mark_full_data_sources_sync_query())

    async def mark_full_agencies_sync(self) -> None:
        await self.execute(get_mark_full_agencies_sync_query())

    @session_manager
    async def get_html_for_url(
        self,
        session: AsyncSession,
        url_id: int
    ) -> str:
        query = (
            select(URLCompressedHTML.compressed_html)
            .where(URLCompressedHTML.url_id == url_id)
        )
        execution_result = await session.execute(query)
        row = execution_result.mappings().one_or_none()
        if row is None:
            return None
        return decompress_html(row["compressed_html"])

    @session_manager
    async def add_raw_html(
        self,
        session: AsyncSession,
        info_list: list[RawHTMLInfo]
    ) -> None:
        for info in info_list:
            compressed_html = URLCompressedHTML(
                url_id=info.url_id,
                compressed_html=compress_html(info.html)
            )
            session.add(compressed_html)

    async def get_data_sources_raw_for_huggingface(self, page: int) -> list[GetForLoadingToHuggingFaceOutput]:
        return await self.run_query_builder(
            GetForLoadingToHuggingFaceQueryBuilder(page)
        )

    async def set_hugging_face_upload_state(self, dt: datetime) -> None:
        await self.run_query_builder(
            SetHuggingFaceUploadStateQueryBuilder(dt=dt)
        )

    async def check_valid_urls_updated(self) -> bool:
        return await self.run_query_builder(
            CheckValidURLsUpdatedQueryBuilder()
        )

    async def get_current_database_time(self) -> datetime:
        return await self.scalar(select(func.now()))

    async def has_urls_without_probe(self) -> bool:
        return await self.run_query_builder(
            HasURLsWithoutProbeQueryBuilder()
        )

    async def get_urls_without_probe(self) -> list[URLMapping]:
        return await self.run_query_builder(
            GetURLsWithoutProbeQueryBuilder()
        )
