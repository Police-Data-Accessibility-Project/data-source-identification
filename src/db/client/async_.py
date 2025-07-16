from datetime import datetime, timedelta
from functools import wraps
from operator import or_
from typing import Optional, Type, Any, List, Sequence

from fastapi import HTTPException
from sqlalchemy import select, exists, func, case, Select, and_, update, delete, literal, text, Row
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload, QueryableAttribute, aliased
from sqlalchemy.sql.functions import coalesce
from starlette import status

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
from src.api.endpoints.batch.dtos.get.summaries.response import GetBatchSummariesResponse
from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary
from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.api.endpoints.metrics.dtos.get.backlog import GetMetricsBacklogResponseDTO, GetMetricsBacklogResponseInnerDTO
from src.api.endpoints.metrics.dtos.get.batches.aggregated import GetMetricsBatchesAggregatedResponseDTO, \
    GetMetricsBatchesAggregatedInnerResponseDTO
from src.api.endpoints.metrics.dtos.get.batches.breakdown import GetMetricsBatchesBreakdownInnerResponseDTO, \
    GetMetricsBatchesBreakdownResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLsAggregatedResponseDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.pending import GetMetricsURLsBreakdownPendingResponseDTO, \
    GetMetricsURLsBreakdownPendingResponseInnerDTO
from src.api.endpoints.metrics.dtos.get.urls.breakdown.submitted import GetMetricsURLsBreakdownSubmittedResponseDTO, \
    GetMetricsURLsBreakdownSubmittedInnerDTO
from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.approve.query import ApproveURLQueryBuilder
from src.api.endpoints.review.enums import RejectionReason
from src.api.endpoints.review.next.dto import GetNextURLForFinalReviewOuterResponse
from src.api.endpoints.review.reject.query import RejectURLQueryBuilder
from src.api.endpoints.search.dtos.response import SearchURLResponse
from src.api.endpoints.task.dtos.get.task import TaskInfo
from src.api.endpoints.task.dtos.get.tasks import GetTasksResponse, GetTasksResponseTaskInfo
from src.api.endpoints.url.dtos.response import GetURLsResponseInfo, GetURLsResponseErrorInfo, GetURLsResponseInnerInfo
from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus, SuggestionType, RecordType, SuggestedStatus
from src.core.env_var_manager import EnvVarManager
from src.core.tasks.scheduled.operators.agency_sync.dtos.parameters import AgencySyncParameters
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.dtos.tdo import AgencyIdentificationTDO
from src.core.tasks.url.operators.auto_relevant.models.annotation import RelevanceAnnotationInfo
from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO
from src.core.tasks.url.operators.auto_relevant.queries.get_tdos import GetAutoRelevantTDOsQueryBuilder
from src.core.tasks.url.operators.submit_approved_url.tdo import SubmitApprovedURLTDO, SubmittedURLInfo
from src.core.tasks.url.operators.url_404_probe.tdo import URL404ProbeTDO
from src.core.tasks.url.operators.url_duplicate.tdo import URLDuplicateTDO
from src.core.tasks.url.operators.url_miscellaneous_metadata.tdo import URLMiscellaneousMetadataTDO, URLHTMLMetadataInfo
from src.db.client.types import UserSuggestionModel
from src.db.config_manager import ConfigManager
from src.db.constants import PLACEHOLDER_AGENCY_NAME
from src.db.dto_converter import DTOConverter
from src.db.dtos.batch import BatchInfo
from src.db.dtos.duplicate import DuplicateInsertInfo, DuplicateInfo
from src.db.dtos.log import LogInfo, LogOutputInfo
from src.db.dtos.url.annotations.auto.relevancy import AutoRelevancyAnnotationInput
from src.db.dtos.url.core import URLInfo
from src.db.dtos.url.error import URLErrorPydanticInfo
from src.db.dtos.url.html_content import URLHTMLContentInfo, HTMLContentType
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.dtos.url.mapping import URLMapping
from src.db.dtos.url.raw_html import RawHTMLInfo
from src.db.enums import TaskType
from src.db.models.instantiations.agency import Agency
from src.db.models.instantiations.backlog_snapshot import BacklogSnapshot
from src.db.models.instantiations.batch import Batch
from src.db.models.instantiations.confirmed_url_agency import ConfirmedURLAgency
from src.db.models.instantiations.duplicate import Duplicate
from src.db.models.instantiations.link_task_url import LinkTaskURL
from src.db.models.instantiations.log import Log
from src.db.models.instantiations.root_url_cache import RootURL
from src.db.models.instantiations.sync_state_agencies import AgenciesSyncState
from src.db.models.instantiations.task.core import Task
from src.db.models.instantiations.task.error import TaskError
from src.db.models.instantiations.url.checked_for_duplicate import URLCheckedForDuplicate
from src.db.models.instantiations.url.compressed_html import URLCompressedHTML
from src.db.models.instantiations.url.core import URL
from src.db.models.instantiations.url.data_source import URLDataSource
from src.db.models.instantiations.url.error_info import URLErrorInfo
from src.db.models.instantiations.url.html_content import URLHTMLContent
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.instantiations.url.probed_for_404 import URLProbedFor404
from src.db.models.instantiations.url.reviewing_user import ReviewingUserURL
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.auto import AutoRelevantSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.models.templates import Base
from src.db.queries.base.builder import QueryBuilderBase
from src.api.endpoints.review.next.query import GetNextURLForFinalReviewQueryBuilder
from src.db.queries.implementations.core.get.html_content_info import GetHTMLContentInfoQueryBuilder
from src.db.queries.implementations.core.get.recent_batch_summaries.builder import GetRecentBatchSummariesQueryBuilder
from src.db.queries.implementations.core.metrics.urls.aggregated.pending import \
    GetMetricsURLSAggregatedPendingQueryBuilder
from src.db.queries.implementations.core.tasks.agency_sync.upsert import get_upsert_agencies_mappings
from src.db.statement_composer import StatementComposer
from src.db.utils.compression import decompress_html, compress_html
from src.external.pdap.dtos.agencies_sync import AgenciesSyncResponseInnerInfo


def add_standard_limit_and_offset(statement, page, limit=100):
    offset = (page - 1) * limit
    return statement.limit(limit).offset(offset)


class AsyncDatabaseClient:
    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            db_url = EnvVarManager.get().get_postgres_connection_string(is_async=True)
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
    async def add(self, session: AsyncSession, model: Base):
        session.add(model)

    @session_manager
    async def add_all(self, session: AsyncSession, models: list[Base]):
        session.add_all(models)

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
        model: Base,
        mappings: list[dict],
        id_value: str = "id"
    ):

        query = pg_insert(model)

        set_ = {}
        for k, v in mappings[0].items():
            if k == id_value:
                continue
            set_[k] = getattr(query.excluded, k)

        query = query.on_conflict_do_update(
            index_elements=[id_value],
            set_=set_
        )


        # Note, mapping must include primary key
        await session.execute(
            query,
            mappings
        )

    @session_manager
    async def scalar(self, session: AsyncSession, statement):
        return (await session.execute(statement)).scalar()

    @session_manager
    async def scalars(self, session: AsyncSession, statement):
        return (await session.execute(statement)).scalars().all()

    @session_manager
    async def mapping(self, session: AsyncSession, statement):
        return (await session.execute(statement)).mappings().one()

    @session_manager
    async def run_query_builder(
        self,
        session: AsyncSession,
        builder: QueryBuilderBase
    ) -> Any:
        return await builder.run(session)

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
    ) -> Optional[UserSuggestionModel]:
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
        batch_id: Optional[int],
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

    @session_manager
    async def get_next_url_for_relevance_annotation(
        self,
        session: AsyncSession,
        user_id: int,
        batch_id: Optional[int]
    ) -> GetNextRelevanceAnnotationResponseInfo | None:

        url = await GetNextURLForUserAnnotationQueryBuilder(
            user_suggestion_model_to_exclude=UserRelevantSuggestion,
            auto_suggestion_relationship=URL.auto_relevant_suggestion,
            batch_id=batch_id
        ).run(session)
        if url is None:
            return None

        # Next, get all HTML content for the URL
        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        if url.auto_relevant_suggestion is not None:
            suggestion = url.auto_relevant_suggestion
        else:
            suggestion = None

        return GetNextRelevanceAnnotationResponseInfo(
            url_info=URLMapping(
                url=url.url,
                url_id=url.id
            ),
            annotation=RelevanceAnnotationInfo(
                is_relevant=suggestion.relevant,
                confidence=suggestion.confidence,
                model_name=suggestion.model_name
            ) if suggestion is not None else None,
            html_info=html_response_info,
            batch_info=await GetAnnotationBatchInfoQueryBuilder(
                batch_id=batch_id,
                models=[
                    UserUrlAgencySuggestion,
                ]
            ).run(session)
        )

    # endregion relevant

    # region record_type

    @session_manager
    async def get_next_url_for_record_type_annotation(
        self,
        session: AsyncSession,
        user_id: int,
        batch_id: Optional[int]
    ) -> Optional[GetNextRecordTypeAnnotationResponseInfo]:

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
            url.outcome = URLStatus.ERROR.value

            url_error = URLErrorInfo(**url_error_info.model_dump())
            session.add(url_error)

    @session_manager
    async def get_urls_with_errors(self, session: AsyncSession) -> list[URLErrorPydanticInfo]:
        statement = (select(URL, URLErrorInfo.error, URLErrorInfo.updated_at, URLErrorInfo.task_id)
                     .join(URLErrorInfo)
                     .where(URL.outcome == URLStatus.ERROR.value)
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
    async def has_pending_urls_without_html_data(self, session: AsyncSession) -> bool:
        statement = self.statement_composer.pending_urls_without_html_data()
        statement = statement.limit(1)
        scalar_result = await session.scalars(statement)
        return bool(scalar_result.first())

    @session_manager
    async def has_pending_urls_missing_miscellaneous_metadata(self, session: AsyncSession) -> bool:
        query = StatementComposer.pending_urls_missing_miscellaneous_metadata_query()
        query = query.limit(1)

        scalar_result = await session.scalars(query)
        return bool(scalar_result.first())

    @session_manager
    async def get_pending_urls_missing_miscellaneous_metadata(
        self,
        session: AsyncSession
    ) -> list[URLMiscellaneousMetadataTDO]:
        query = StatementComposer.pending_urls_missing_miscellaneous_metadata_query()
        query = (
            query.options(
                selectinload(URL.batch),
                selectinload(URL.html_content)
            ).limit(100).order_by(URL.id)
        )

        scalar_result = await session.scalars(query)
        all_results = scalar_result.all()
        final_results = []
        for result in all_results:
            tdo = URLMiscellaneousMetadataTDO(
                url_id=result.id,
                collector_metadata=result.collector_metadata or {},
                collector_type=CollectorType(result.batch.strategy),
            )
            html_info = URLHTMLMetadataInfo()
            for html_content in result.html_content:
                if html_content.content_type == HTMLContentType.TITLE.value:
                    html_info.title = html_content.content
                elif html_content.content_type == HTMLContentType.DESCRIPTION.value:
                    html_info.description = html_content.content
            tdo.html_metadata_info = html_info
            final_results.append(tdo)
        return final_results

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

    @session_manager
    async def get_pending_urls_without_html_data(self, session: AsyncSession) -> list[URLInfo]:
        # TODO: Add test that includes some urls WITH html data. Check they're not returned
        statement = self.statement_composer.pending_urls_without_html_data()
        statement = statement.limit(100).order_by(URL.id)
        scalar_result = await session.scalars(statement)
        results: list[URL] = scalar_result.all()
        return DTOConverter.url_list_to_url_info_list(results)

    async def get_urls_with_html_data_and_without_models(
        self,
        session: AsyncSession,
        model: Type[Base]
    ):
        statement = (select(URL)
                     .options(selectinload(URL.html_content))
                     .where(URL.outcome == URLStatus.PENDING.value))
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
                     .where(URL.outcome == URLStatus.PENDING.value))
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
        order_by_attribute: Optional[str] = None
    ) -> list[Base]:
        """
        Get all records of a model
        Used primarily in testing
        """
        statement = select(model)
        if order_by_attribute:
            statement = statement.order_by(getattr(model, order_by_attribute))
        result = await session.execute(statement)
        return result.scalars().all()

    @session_manager
    async def load_root_url_cache(self, session: AsyncSession) -> dict[str, str]:
        statement = select(RootURL)
        scalar_result = await session.scalars(statement)
        model_result = scalar_result.all()
        d = {}
        for result in model_result:
            d[result.url] = result.page_title
        return d

    async def add_to_root_url_cache(self, url: str, page_title: str) -> None:
        cache = RootURL(url=url, page_title=page_title)
        await self.add(cache)

    @session_manager
    async def get_urls(self, session: AsyncSession, page: int, errors: bool) -> GetURLsResponseInfo:
        statement = select(URL).options(
            selectinload(URL.error_info)
        ).order_by(URL.id)
        if errors:
            # Only return URLs with errors
            statement = statement.where(
                exists(
                    select(URLErrorInfo).where(URLErrorInfo.url_id == URL.id)
                )
            )
        add_standard_limit_and_offset(statement, page)
        execute_result = await session.execute(statement)
        all_results = execute_result.scalars().all()
        final_results = []
        for result in all_results:
            error_results = []
            for error in result.error_info:
                error_result = GetURLsResponseErrorInfo(
                    id=error.id,
                    error=error.error,
                    updated_at=error.updated_at
                )
                error_results.append(error_result)
            final_results.append(
                GetURLsResponseInnerInfo(
                    id=result.id,
                    batch_id=result.batch_id,
                    url=result.url,
                    status=URLStatus(result.outcome),
                    collector_metadata=result.collector_metadata,
                    updated_at=result.updated_at,
                    created_at=result.created_at,
                    errors=error_results,
                )
            )

        return GetURLsResponseInfo(
            urls=final_results,
            count=len(final_results)
        )

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

    @session_manager
    async def get_task_info(self, session: AsyncSession, task_id: int) -> TaskInfo:
        # Get Task
        result = await session.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.urls),
                selectinload(Task.error),
                selectinload(Task.errored_urls)
            )
        )
        task = result.scalars().first()
        error = task.error[0].error if len(task.error) > 0 else None
        # Get error info if any
        # Get URLs
        urls = task.urls
        url_infos = []
        for url in urls:
            url_info = URLInfo(
                id=url.id,
                batch_id=url.batch_id,
                url=url.url,
                collector_metadata=url.collector_metadata,
                outcome=URLStatus(url.outcome),
                updated_at=url.updated_at
            )
            url_infos.append(url_info)

        errored_urls = []
        for url in task.errored_urls:
            url_error_info = URLErrorPydanticInfo(
                task_id=url.task_id,
                url_id=url.url_id,
                error=url.error,
                updated_at=url.updated_at
            )
            errored_urls.append(url_error_info)
        return TaskInfo(
            task_type=TaskType(task.task_type),
            task_status=BatchStatus(task.task_status),
            error_info=error,
            updated_at=task.updated_at,
            urls=url_infos,
            url_errors=errored_urls
        )

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

    @session_manager
    async def has_urls_without_agency_suggestions(
        self,
        session: AsyncSession
    ) -> bool:
        statement = (
            select(
                URL.id
            ).where(
                URL.outcome == URLStatus.PENDING.value
            )
        )

        statement = self.statement_composer.exclude_urls_with_agency_suggestions(statement)
        raw_result = await session.execute(statement)
        result = raw_result.all()
        return len(result) != 0

    @session_manager
    async def get_urls_without_agency_suggestions(
        self, session: AsyncSession
    ) -> list[AgencyIdentificationTDO]:
        """
        Retrieve URLs without confirmed or suggested agencies
        Args:
            session:

        Returns:

        """

        statement = (
            select(URL.id, URL.collector_metadata, Batch.strategy)
            .where(URL.outcome == URLStatus.PENDING.value)
            .join(Batch)
        )
        statement = self.statement_composer.exclude_urls_with_agency_suggestions(statement)
        statement = statement.limit(100)
        raw_results = await session.execute(statement)
        return [
            AgencyIdentificationTDO(
                url_id=raw_result[0],
                collector_metadata=raw_result[1],
                collector_type=CollectorType(raw_result[2])
            )
            for raw_result in raw_results
        ]

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
            agency = Agency(
                agency_id=suggestion.pdap_agency_id,
                name=suggestion.agency_name,
                state=suggestion.state,
                county=suggestion.county,
                locality=suggestion.locality
            )
            await session.merge(agency)

    @session_manager
    async def add_confirmed_agency_url_links(
        self,
        session: AsyncSession,
        suggestions: list[URLAgencySuggestionInfo]
    ):
        for suggestion in suggestions:
            confirmed_agency = ConfirmedURLAgency(
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
        statement = select(URL).where(exists().where(ConfirmedURLAgency.url_id == URL.id))
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

    @session_manager
    async def get_urls_by_batch(self, session, batch_id: int, page: int = 1) -> List[URLInfo]:
        """Retrieve all URLs associated with a batch."""
        query = Select(URL).where(URL.batch_id == batch_id).order_by(URL.id).limit(100).offset((page - 1) * 100)
        result = await session.execute(query)
        urls = result.scalars().all()
        return ([URLInfo(**url.__dict__) for url in urls])

    @session_manager
    async def insert_url(self, session: AsyncSession, url_info: URLInfo) -> int:
        """Insert a new URL into the database."""
        url_entry = URL(
            batch_id=url_info.batch_id,
            url=url_info.url,
            collector_metadata=url_info.collector_metadata,
            outcome=url_info.outcome.value
        )
        if url_info.created_at is not None:
            url_entry.created_at = url_info.created_at
        session.add(url_entry)
        await session.flush()
        return url_entry.id

    @session_manager
    async def get_url_info_by_url(self, session: AsyncSession, url: str) -> Optional[URLInfo]:
        query = Select(URL).where(URL.url == url)
        raw_result = await session.execute(query)
        url = raw_result.scalars().first()
        return URLInfo(**url.__dict__)

    @session_manager
    async def get_url_info_by_id(self, session: AsyncSession, url_id: int) -> Optional[URLInfo]:
        query = Select(URL).where(URL.id == url_id)
        raw_result = await session.execute(query)
        url = raw_result.scalars().first()
        return URLInfo(**url.__dict__)

    @session_manager
    async def insert_logs(self, session, log_infos: List[LogInfo]):
        for log_info in log_infos:
            log = Log(log=log_info.log, batch_id=log_info.batch_id)
            if log_info.created_at is not None:
                log.created_at = log_info.created_at
            session.add(log)

    @session_manager
    async def insert_duplicates(self, session, duplicate_infos: list[DuplicateInsertInfo]):
        for duplicate_info in duplicate_infos:
            duplicate = Duplicate(
                batch_id=duplicate_info.duplicate_batch_id,
                original_url_id=duplicate_info.original_url_id,
            )
            session.add(duplicate)

    @session_manager
    async def insert_batch(self, session: AsyncSession, batch_info: BatchInfo) -> int:
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

    async def insert_urls(self, url_infos: List[URLInfo], batch_id: int) -> InsertURLsInfo:
        url_mappings = []
        duplicates = []
        for url_info in url_infos:
            url_info.batch_id = batch_id
            try:
                url_id = await self.insert_url(url_info)
                url_mappings.append(URLMapping(url_id=url_id, url=url_info.url))
            except IntegrityError:
                orig_url_info = await self.get_url_info_by_url(url_info.url)
                duplicate_info = DuplicateInsertInfo(
                    duplicate_batch_id=batch_id,
                    original_url_id=orig_url_info.id
                )
                duplicates.append(duplicate_info)
        await self.insert_duplicates(duplicates)

        return InsertURLsInfo(
            url_mappings=url_mappings,
            total_count=len(url_infos),
            original_count=len(url_mappings),
            duplicate_count=len(duplicates),
            url_ids=[url_mapping.url_id for url_mapping in url_mappings]
        )

    @session_manager
    async def update_batch_post_collection(
        self,
        session,
        batch_id: int,
        total_url_count: int,
        original_url_count: int,
        duplicate_url_count: int,
        batch_status: BatchStatus,
        compute_time: float = None,
    ):

        query = Select(Batch).where(Batch.id == batch_id)
        result = await session.execute(query)
        batch = result.scalars().first()

        batch.total_url_count = total_url_count
        batch.original_url_count = original_url_count
        batch.duplicate_url_count = duplicate_url_count
        batch.status = batch_status.value
        batch.compute_time = compute_time

    @session_manager
    async def has_validated_urls(self, session: AsyncSession) -> bool:
        query = (
            select(URL)
            .where(URL.outcome == URLStatus.VALIDATED.value)
        )
        urls = await session.execute(query)
        urls = urls.scalars().all()
        return len(urls) > 0

    @session_manager
    async def get_validated_urls(
        self,
        session: AsyncSession
    ) -> list[SubmitApprovedURLTDO]:
        query = (
            select(URL)
            .where(URL.outcome == URLStatus.VALIDATED.value)
            .options(
                selectinload(URL.optional_data_source_metadata),
                selectinload(URL.confirmed_agencies),
                selectinload(URL.reviewing_user)
            ).limit(100)
        )
        urls = await session.execute(query)
        urls = urls.scalars().all()
        results: list[SubmitApprovedURLTDO] = []
        for url in urls:
            agency_ids = []
            for agency in url.confirmed_agencies:
                agency_ids.append(agency.agency_id)
            optional_metadata = url.optional_data_source_metadata

            if optional_metadata is None:
                record_formats = None
                data_portal_type = None
                supplying_entity = None
            else:
                record_formats = optional_metadata.record_formats
                data_portal_type = optional_metadata.data_portal_type
                supplying_entity = optional_metadata.supplying_entity

            tdo = SubmitApprovedURLTDO(
                url_id=url.id,
                url=url.url,
                name=url.name,
                agency_ids=agency_ids,
                description=url.description,
                record_type=url.record_type,
                record_formats=record_formats,
                data_portal_type=data_portal_type,
                supplying_entity=supplying_entity,
                approving_user_id=url.reviewing_user.user_id
            )
            results.append(tdo)
        return results

    @session_manager
    async def mark_urls_as_submitted(self, session: AsyncSession, infos: list[SubmittedURLInfo]):
        for info in infos:
            url_id = info.url_id
            data_source_id = info.data_source_id

            query = (
                update(URL)
                .where(URL.id == url_id)
                .values(
                    outcome=URLStatus.SUBMITTED.value
                )
            )

            url_data_source_object = URLDataSource(
                url_id=url_id,
                data_source_id=data_source_id
            )
            if info.submitted_at is not None:
                url_data_source_object.created_at = info.submitted_at
            session.add(url_data_source_object)

            await session.execute(query)

    @session_manager
    async def get_duplicates_by_batch_id(self, session, batch_id: int, page: int) -> List[DuplicateInfo]:
        original_batch = aliased(Batch)
        duplicate_batch = aliased(Batch)

        query = (
            Select(
                URL.url.label("source_url"),
                URL.id.label("original_url_id"),
                duplicate_batch.id.label("duplicate_batch_id"),
                duplicate_batch.parameters.label("duplicate_batch_parameters"),
                original_batch.id.label("original_batch_id"),
                original_batch.parameters.label("original_batch_parameters"),
            )
            .select_from(Duplicate)
            .join(URL, Duplicate.original_url_id == URL.id)
            .join(duplicate_batch, Duplicate.batch_id == duplicate_batch.id)
            .join(original_batch, URL.batch_id == original_batch.id)
            .filter(duplicate_batch.id == batch_id)
            .limit(100)
            .offset((page - 1) * 100)
        )
        raw_results = await session.execute(query)
        results = raw_results.all()
        final_results = []
        for result in results:
            final_results.append(
                DuplicateInfo(
                    source_url=result.source_url,
                    duplicate_batch_id=result.duplicate_batch_id,
                    duplicate_metadata=result.duplicate_batch_parameters,
                    original_batch_id=result.original_batch_id,
                    original_metadata=result.original_batch_parameters,
                    original_url_id=result.original_url_id
                )
            )
        return final_results

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

    @session_manager
    async def upload_manual_batch(
        self,
        session: AsyncSession,
        user_id: int,
        dto: ManualBatchInputDTO
    ) -> ManualBatchResponseDTO:
        batch = Batch(
            strategy=CollectorType.MANUAL.value,
            status=BatchStatus.READY_TO_LABEL.value,
            parameters={
                "name": dto.name
            },
            user_id=user_id
        )
        session.add(batch)
        await session.flush()

        batch_id = batch.id
        url_ids = []
        duplicate_urls = []

        for entry in dto.entries:
            url = URL(
                url=entry.url,
                name=entry.name,
                description=entry.description,
                batch_id=batch_id,
                collector_metadata=entry.collector_metadata,
                outcome=URLStatus.PENDING.value,
                record_type=entry.record_type.value if entry.record_type is not None else None,
            )

            async with session.begin_nested():
                try:
                    session.add(url)
                    await session.flush()
                except IntegrityError:
                    duplicate_urls.append(entry.url)
                    continue
            await session.flush()
            optional_metadata = URLOptionalDataSourceMetadata(
                url_id=url.id,
                record_formats=entry.record_formats,
                data_portal_type=entry.data_portal_type,
                supplying_entity=entry.supplying_entity,
            )
            session.add(optional_metadata)
            url_ids.append(url.id)

        return ManualBatchResponseDTO(
            batch_id=batch_id,
            urls=url_ids,
            duplicate_urls=duplicate_urls
        )

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

    @session_manager
    async def get_batches_aggregated_metrics(self, session: AsyncSession) -> GetMetricsBatchesAggregatedResponseDTO:
        sc = StatementComposer

        # First, get all batches broken down by collector type and status
        def batch_column(status: BatchStatus, label):
            return sc.count_distinct(
                case(
                    (
                        Batch.status == status.value,
                        Batch.id
                    )
                ),
                label=label
            )

        batch_count_subquery = select(
            batch_column(BatchStatus.READY_TO_LABEL, label="done_count"),
            batch_column(BatchStatus.ERROR, label="error_count"),
            Batch.strategy,
        ).group_by(Batch.strategy).subquery("batch_count")

        def url_column(status: URLStatus, label):
            return sc.count_distinct(
                case(
                    (
                        URL.outcome == status.value,
                        URL.id
                    )
                ),
                label=label
            )

        # Next, count urls
        url_count_subquery = select(
            Batch.strategy,
            url_column(URLStatus.PENDING, label="pending_count"),
            url_column(URLStatus.ERROR, label="error_count"),
            url_column(URLStatus.VALIDATED, label="validated_count"),
            url_column(URLStatus.SUBMITTED, label="submitted_count"),
            url_column(URLStatus.NOT_RELEVANT, label="rejected_count"),

        ).outerjoin(
            Batch, Batch.id == URL.batch_id
        ).group_by(
            Batch.strategy
        ).subquery("url_count")

        # Combine
        query = select(
            Batch.strategy,
            batch_count_subquery.c.done_count.label("batch_done_count"),
            batch_count_subquery.c.error_count.label("batch_error_count"),
            coalesce(url_count_subquery.c.pending_count, 0).label("pending_count"),
            coalesce(url_count_subquery.c.error_count, 0).label("error_count"),
            coalesce(url_count_subquery.c.submitted_count, 0).label("submitted_count"),
            coalesce(url_count_subquery.c.rejected_count, 0).label("rejected_count"),
            coalesce(url_count_subquery.c.validated_count, 0).label("validated_count")
        ).join(
            batch_count_subquery,
            Batch.strategy == batch_count_subquery.c.strategy
        ).outerjoin(
            url_count_subquery,
            Batch.strategy == url_count_subquery.c.strategy
        )
        raw_results = await session.execute(query)
        results = raw_results.all()
        d: dict[CollectorType, GetMetricsBatchesAggregatedInnerResponseDTO] = {}
        for result in results:
            d[CollectorType(result.strategy)] = GetMetricsBatchesAggregatedInnerResponseDTO(
                count_successful_batches=result.batch_done_count,
                count_failed_batches=result.batch_error_count,
                count_urls=result.pending_count + result.submitted_count +
                           result.rejected_count + result.error_count +
                           result.validated_count,
                count_urls_pending=result.pending_count,
                count_urls_validated=result.validated_count,
                count_urls_submitted=result.submitted_count,
                count_urls_rejected=result.rejected_count,
                count_urls_errors=result.error_count
            )

        total_batch_query = await session.execute(
            select(
                sc.count_distinct(Batch.id, label="count")
            )
        )
        total_batch_count = total_batch_query.scalars().one_or_none()
        if total_batch_count is None:
            total_batch_count = 0

        return GetMetricsBatchesAggregatedResponseDTO(
            total_batches=total_batch_count,
            by_strategy=d
        )

    @session_manager
    async def get_batches_breakdown_metrics(
        self,
        session: AsyncSession,
        page: int
    ) -> GetMetricsBatchesBreakdownResponseDTO:
        sc = StatementComposer

        main_query = select(
            Batch.strategy,
            Batch.id,
            Batch.status,
            Batch.date_generated.label("created_at"),
        )

        def url_column(status: URLStatus, label):
            return sc.count_distinct(
                case(
                    (
                        URL.outcome == status.value,
                        URL.id
                    )
                ),
                label=label
            )

        count_query = select(
            URL.batch_id,
            sc.count_distinct(URL.id, label="count_total"),
            url_column(URLStatus.PENDING, label="count_pending"),
            url_column(URLStatus.SUBMITTED, label="count_submitted"),
            url_column(URLStatus.NOT_RELEVANT, label="count_rejected"),
            url_column(URLStatus.ERROR, label="count_error"),
            url_column(URLStatus.VALIDATED, label="count_validated"),
        ).group_by(
            URL.batch_id
        ).subquery("url_count")

        query = (select(
            main_query.c.strategy,
            main_query.c.id,
            main_query.c.created_at,
            main_query.c.status,
            coalesce(count_query.c.count_total, 0).label("count_total"),
            coalesce(count_query.c.count_pending, 0).label("count_pending"),
            coalesce(count_query.c.count_submitted, 0).label("count_submitted"),
            coalesce(count_query.c.count_rejected, 0).label("count_rejected"),
            coalesce(count_query.c.count_error, 0).label("count_error"),
            coalesce(count_query.c.count_validated, 0).label("count_validated"),
        ).outerjoin(
            count_query,
            main_query.c.id == count_query.c.batch_id
        ).offset(
            (page - 1) * 100
        ).order_by(
            main_query.c.created_at.asc()
        ))

        raw_results = await session.execute(query)
        results = raw_results.all()
        batches: list[GetMetricsBatchesBreakdownInnerResponseDTO] = []
        for result in results:
            dto = GetMetricsBatchesBreakdownInnerResponseDTO(
                batch_id=result.id,
                strategy=CollectorType(result.strategy),
                status=BatchStatus(result.status),
                created_at=result.created_at,
                count_url_total=result.count_total,
                count_url_pending=result.count_pending,
                count_url_submitted=result.count_submitted,
                count_url_rejected=result.count_rejected,
                count_url_error=result.count_error,
                count_url_validated=result.count_validated
            )
            batches.append(dto)
        return GetMetricsBatchesBreakdownResponseDTO(
            batches=batches,
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
            URL.outcome == URLStatus.PENDING.value
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
                        URL.outcome == status.value,
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

    def compile(self, statement):
        compiled_sql = statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        return compiled_sql

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
            .where(URL.outcome == URLStatus.PENDING.value)
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
            URL.outcome == URLStatus.PENDING.value
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

    @session_manager
    async def has_pending_urls_not_checked_for_duplicates(self, session: AsyncSession) -> bool:
        query = (select(
            URL.id
        ).outerjoin(
            URLCheckedForDuplicate,
            URL.id == URLCheckedForDuplicate.url_id
        ).where(
            URL.outcome == URLStatus.PENDING.value,
            URLCheckedForDuplicate.id == None
        ).limit(1)
                 )

        raw_result = await session.execute(query)
        result = raw_result.one_or_none()
        return result is not None

    @session_manager
    async def get_pending_urls_not_checked_for_duplicates(self, session: AsyncSession) -> List[URLDuplicateTDO]:
        query = (select(
            URL
        ).outerjoin(
            URLCheckedForDuplicate,
            URL.id == URLCheckedForDuplicate.url_id
        ).where(
            URL.outcome == URLStatus.PENDING.value,
            URLCheckedForDuplicate.id == None
        ).limit(100)
                 )

        raw_result = await session.execute(query)
        urls = raw_result.scalars().all()
        return [URLDuplicateTDO(url=url.url, url_id=url.id) for url in urls]

    async def mark_all_as_duplicates(self, url_ids: List[int]):
        query = update(URL).where(URL.id.in_(url_ids)).values(outcome=URLStatus.DUPLICATE.value)
        await self.execute(query)

    async def mark_all_as_404(self, url_ids: List[int]):
        query = update(URL).where(URL.id.in_(url_ids)).values(outcome=URLStatus.NOT_FOUND.value)
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
                    URL.outcome == URLStatus.PENDING.value,
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
                    URL.outcome == URLStatus.PENDING.value,
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

    @session_manager
    async def get_urls_aggregated_pending_metrics(
        self,
        session: AsyncSession
    ):
        builder = GetMetricsURLSAggregatedPendingQueryBuilder()
        result = await builder.run(
            session=session
        )
        return result

    @session_manager
    async def get_agencies_sync_parameters(
        self,
        session: AsyncSession
    ) -> AgencySyncParameters:
        query = select(
            AgenciesSyncState.current_page,
            AgenciesSyncState.current_cutoff_date
        )
        try:
            result = (await session.execute(query)).mappings().one()
            return AgencySyncParameters(
                page=result['current_page'],
                cutoff_date=result['current_cutoff_date']
            )
        except NoResultFound:
            # Add value
            state = AgenciesSyncState()
            session.add(state)
            return AgencySyncParameters(page=None, cutoff_date=None)



    async def upsert_agencies(
        self,
        agencies: list[AgenciesSyncResponseInnerInfo]
    ):
        await self.bulk_upsert(
            model=Agency,
            mappings=get_upsert_agencies_mappings(agencies),
            id_value="agency_id",
        )

    async def update_agencies_sync_progress(self, page: int):
        query = update(
            AgenciesSyncState
        ).values(
            current_page=page
        )
        await self.execute(query)

    async def mark_full_agencies_sync(self):
        query = update(
            AgenciesSyncState
        ).values(
            last_full_sync_at=func.now(),
            current_cutoff_date=func.now() - text('interval \'1 day\''),
            current_page=None
        )
        await self.execute(query)

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
    ):
        for info in info_list:
            compressed_html = URLCompressedHTML(
                url_id=info.url_id,
                compressed_html=compress_html(info.html)
            )
            session.add(compressed_html)
