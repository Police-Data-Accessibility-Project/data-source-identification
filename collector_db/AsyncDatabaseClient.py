from datetime import datetime, timedelta
from functools import wraps
from operator import or_
from typing import Optional, Type, Any, List

from fastapi import HTTPException
from sqlalchemy import select, exists, func, case, desc, Select, not_, and_, update, asc, delete, insert, CTE, literal
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload, QueryableAttribute, aliased
from sqlalchemy.sql.functions import coalesce
from starlette import status

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOConverter import DTOConverter
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInsertInfo, DuplicateInfo
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.LogInfo import LogInfo, LogOutputInfo
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo, HTMLContentType
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.StatementComposer import StatementComposer
from collector_db.constants import PLACEHOLDER_AGENCY_NAME
from collector_db.enums import TaskType
from collector_db.models import URL, URLErrorInfo, URLHTMLContent, Base, \
    RootURL, Task, TaskError, LinkTaskURL, Batch, Agency, AutomatedUrlAgencySuggestion, \
    UserUrlAgencySuggestion, AutoRelevantSuggestion, AutoRecordTypeSuggestion, UserRelevantSuggestion, \
    UserRecordTypeSuggestion, ReviewingUserURL, URLOptionalDataSourceMetadata, ConfirmedURLAgency, Duplicate, Log, \
    BacklogSnapshot, URLDataSource, URLCheckedForDuplicate, URLProbedFor404
from collector_manager.enums import URLStatus, CollectorType
from core.DTOs.AllAnnotationPostInfo import AllAnnotationPostInfo
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.GetMetricsBacklogResponse import GetMetricsBacklogResponseDTO, GetMetricsBacklogResponseInnerDTO
from core.DTOs.GetMetricsBatchesAggregatedResponseDTO import GetMetricsBatchesAggregatedResponseDTO, \
    GetMetricsBatchesAggregatedInnerResponseDTO
from core.DTOs.GetMetricsBatchesBreakdownResponseDTO import GetMetricsBatchesBreakdownResponseDTO, \
    GetMetricsBatchesBreakdownInnerResponseDTO
from core.DTOs.GetMetricsURLsAggregatedResponseDTO import GetMetricsURLsAggregatedResponseDTO
from core.DTOs.GetMetricsURLsBreakdownPendingResponseDTO import GetMetricsURLsBreakdownPendingResponseDTO, \
    GetMetricsURLsBreakdownPendingResponseInnerDTO
from core.DTOs.GetMetricsURLsBreakdownSubmittedResponseDTO import GetMetricsURLsBreakdownSubmittedResponseDTO, \
    GetMetricsURLsBreakdownSubmittedInnerDTO
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    GetNextURLForAgencyAgencyInfo, GetNextURLForAgencyAnnotationInnerResponse
from core.DTOs.GetNextURLForAllAnnotationResponse import GetNextURLForAllAnnotationResponse, \
    GetNextURLForAllAnnotationInnerResponse
from core.DTOs.GetNextURLForFinalReviewResponse import GetNextURLForFinalReviewResponse, FinalReviewAnnotationInfo, \
    FinalReviewOptionalMetadata
from core.DTOs.GetTasksResponse import GetTasksResponse, GetTasksResponseTaskInfo
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo, GetURLsResponseErrorInfo, \
    GetURLsResponseInnerInfo
from core.DTOs.ManualBatchInputDTO import ManualBatchInputDTO
from core.DTOs.ManualBatchResponseDTO import ManualBatchResponseDTO
from core.DTOs.SearchURLResponse import SearchURLResponse
from core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from core.DTOs.task_data_objects.AgencyIdentificationTDO import AgencyIdentificationTDO
from core.DTOs.task_data_objects.SubmitApprovedURLTDO import SubmitApprovedURLTDO, SubmittedURLInfo
from core.DTOs.task_data_objects.URL404ProbeTDO import URL404ProbeTDO
from core.DTOs.task_data_objects.URLDuplicateTDO import URLDuplicateTDO
from core.DTOs.task_data_objects.URLMiscellaneousMetadataTDO import URLMiscellaneousMetadataTDO, URLHTMLMetadataInfo
from core.EnvVarManager import EnvVarManager
from core.enums import BatchStatus, SuggestionType, RecordType
from html_tag_collector.DataClassTags import convert_to_response_html_info

# Type Hints

UserSuggestionModel = UserRelevantSuggestion or UserRecordTypeSuggestion or UserUrlAgencySuggestion
AutoSuggestionModel = AutoRelevantSuggestion or AutoRecordTypeSuggestion or AutomatedUrlAgencySuggestion


def add_standard_limit_and_offset(statement, page, limit=100):
    offset = (page - 1) * limit
    return statement.limit(limit).offset(offset)


class AsyncDatabaseClient:
    def __init__(self, db_url: Optional[str] = None):
        if db_url is None:
            db_url = EnvVarManager.get().get_postgres_connection_string(is_async=True)
        self.engine = create_async_engine(
            url=db_url,
            echo=ConfigManager.get_sqlalchemy_echo(),
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

    # region relevant
    @session_manager
    async def add_auto_relevant_suggestion(
            self,
            session: AsyncSession,
            url_id: int,
            relevant: bool
    ):
        suggestion = AutoRelevantSuggestion(
            url_id=url_id,
            relevant=relevant
        )
        session.add(suggestion)

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

    @staticmethod
    async def get_next_url_for_user_annotation(
            session: AsyncSession,
            user_suggestion_model_to_exclude: UserSuggestionModel,
            auto_suggestion_relationship: QueryableAttribute,
            batch_id: Optional[int],
            check_if_annotated_not_relevant: bool = False
    ) -> URL:
        url_query = (
            select(
                URL,
            )
            .where(URL.outcome == URLStatus.PENDING.value)
            # URL must not have user suggestion
            .where(
                StatementComposer.user_suggestion_not_exists(user_suggestion_model_to_exclude)
            )
        )

        if check_if_annotated_not_relevant:
            url_query = url_query.where(
                not_(
                    exists(
                        select(UserRelevantSuggestion)
                        .where(
                            UserRelevantSuggestion.url_id == URL.id,
                            UserRelevantSuggestion.relevant == False
                        )
                    )
                )
            )

        if batch_id is not None:
            url_query = url_query.where(URL.batch_id == batch_id)

        url_query = url_query.options(
                joinedload(auto_suggestion_relationship),
                joinedload(URL.html_content)
            ).limit(1)

        raw_result = await session.execute(url_query)

        return raw_result.unique().scalars().one_or_none()

    @session_manager
    async def add_user_relevant_suggestion(
            self,
            session: AsyncSession,
            url_id: int,
            user_id: int,
            relevant: bool
    ):
        prior_suggestion = await self.get_user_suggestion(
            session,
            model=UserRelevantSuggestion,
            user_id=user_id,
            url_id=url_id
        )
        if prior_suggestion is not None:
            prior_suggestion.relevant = relevant
            return

        suggestion = UserRelevantSuggestion(
            url_id=url_id,
            user_id=user_id,
            relevant=relevant
        )
        session.add(suggestion)

    @session_manager
    async def get_next_url_for_relevance_annotation(
            self,
            session: AsyncSession,
            user_id: int,
            batch_id: Optional[int]
    ) -> Optional[GetNextRelevanceAnnotationResponseInfo]:

        url = await self.get_next_url_for_user_annotation(
            session,
            user_suggestion_model_to_exclude=UserRelevantSuggestion,
            auto_suggestion_relationship=URL.auto_relevant_suggestion,
            batch_id=batch_id
        )
        if url is None:
            return None

        # Next, get all HTML content for the URL
        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        if url.auto_relevant_suggestion is not None:
            suggestion = url.auto_relevant_suggestion.relevant
        else:
            suggestion = None

        return GetNextRelevanceAnnotationResponseInfo(
            url_info=URLMapping(
                url=url.url,
                url_id=url.id
            ),
            suggested_relevant=suggestion,
            html_info=html_response_info
        )

    #endregion relevant

    #region record_type

    @session_manager
    async def get_next_url_for_record_type_annotation(
            self,
            session: AsyncSession,
            user_id: int,
            batch_id: Optional[int]
    ) -> Optional[GetNextRecordTypeAnnotationResponseInfo]:

        url = await self.get_next_url_for_user_annotation(
            session,
            user_suggestion_model_to_exclude=UserRecordTypeSuggestion,
            auto_suggestion_relationship=URL.auto_record_type_suggestion,
            batch_id=batch_id,
            check_if_annotated_not_relevant=True
        )
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
            html_info=html_response_info
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

    @session_manager
    async def add_auto_record_type_suggestion(
            self,
            session: AsyncSession,
            url_id: int,
            record_type: RecordType
    ):

        suggestion = AutoRecordTypeSuggestion(
            url_id=url_id,
            record_type=record_type.value
        )
        session.add(suggestion)

    @session_manager
    async def add_auto_relevance_suggestions(
            self,
            session: AsyncSession,
            url_and_relevance_type_list: list[tuple[int, bool]]
    ):
        for url_id, relevant in url_and_relevance_type_list:
            suggestion = AutoRelevantSuggestion(
                url_id=url_id,
                relevant=relevant
            )
            session.add(suggestion)

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

    #endregion record_type

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
            final_results.append(URLErrorPydanticInfo(
                url_id=url.id,
                error=error,
                updated_at=updated_at,
                task_id=task_id
            ))

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
        urls: list[URL] = raw_result.unique().scalars().all()
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

    @session_manager
    async def get_urls_with_html_data_and_without_auto_relevant_suggestion(
            self,
            session: AsyncSession
    ):
        return await self.get_urls_with_html_data_and_without_models(
            session=session,
            model=AutoRelevantSuggestion
        )

    async def has_urls_with_html_data_and_without_models(
            self,
            session: AsyncSession,
            model: Type[Base]
    ) -> bool:
        statement = (select(URL)
                     .join(URLHTMLContent)
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
    async def has_urls_with_html_data_and_without_auto_record_type_suggestion(self, session: AsyncSession) -> bool:
        return await self.has_urls_with_html_data_and_without_models(
            session=session,
            model=AutoRecordTypeSuggestion
        )

    @session_manager
    async def has_urls_with_html_data_and_without_auto_relevant_suggestion(self, session: AsyncSession) -> bool:
        return await self.has_urls_with_html_data_and_without_models(
            session=session,
            model=AutoRelevantSuggestion
        )


    @session_manager
    async def get_all(self, session, model: Base, order_by_attribute: Optional[str] = None) -> list[Base]:
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

    @session_manager
    async def add_to_root_url_cache(self, session: AsyncSession, url: str, page_title: str) -> None:
        cache = RootURL(url=url, page_title=page_title)
        session.add(cache)

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
        await session.commit()

    @session_manager
    async def add_task_error(self, session: AsyncSession, task_id: int, error: str):
        task_error = TaskError(
            task_id=task_id,
            error=error
        )
        session.add(task_error)
        await session.commit()

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

    @session_manager
    async def get_html_content_info(self, session: AsyncSession, url_id: int) -> list[URLHTMLContentInfo]:
        session_result = await session.execute(
            select(URLHTMLContent)
            .where(URLHTMLContent.url_id == url_id)
        )
        results = session_result.scalars().all()
        return [URLHTMLContentInfo(**result.__dict__) for result in results]

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
    async def get_urls_without_agency_suggestions(self, session: AsyncSession) -> list[AgencyIdentificationTDO]:
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

    @session_manager
    async def get_next_url_agency_for_annotation(
            self,
            session: AsyncSession,
            user_id: int,
            batch_id: Optional[int]
    ) -> GetNextURLForAgencyAnnotationResponse:
        """
        Retrieve URL for annotation
        The URL must
            not be a confirmed URL
            not have been annotated by this user
            have extant autosuggestions
        """
        # Select statement
        statement = (
            select(URL.id, URL.url)
            # Must not have confirmed agencies
            .where(
                URL.outcome == URLStatus.PENDING.value
            )
        )

        if batch_id is not None:
            statement = statement.where(URL.batch_id == batch_id)

        # Must not have been annotated by a user
        statement = (
            statement.join(UserUrlAgencySuggestion, isouter=True)
            .where(
                ~exists(
                    select(UserUrlAgencySuggestion).
                    where(UserUrlAgencySuggestion.url_id == URL.id).
                    correlate(URL)
                )
            )
            # Must have extant autosuggestions
            .join(AutomatedUrlAgencySuggestion, isouter=True)
            .where(
                exists(
                    select(AutomatedUrlAgencySuggestion).
                    where(AutomatedUrlAgencySuggestion.url_id == URL.id).
                    correlate(URL)
                )
            )
            # Must not have confirmed agencies
            .join(ConfirmedURLAgency, isouter=True)
            .where(
                ~exists(
                    select(ConfirmedURLAgency).
                    where(ConfirmedURLAgency.url_id == URL.id).
                    correlate(URL)
                )
            )
            # Must not have been marked as "Not Relevant" by this user
            .join(UserRelevantSuggestion, isouter=True)
            .where(
                ~exists(
                    select(UserRelevantSuggestion).
                    where(
                        (UserRelevantSuggestion.user_id == user_id) &
                        (UserRelevantSuggestion.url_id == URL.id) &
                        (UserRelevantSuggestion.relevant == False)
                    ).correlate(URL)
                )
            )
        ).limit(1)
        raw_result = await session.execute(statement)
        results = raw_result.all()
        if len(results) == 0:
            return GetNextURLForAgencyAnnotationResponse(
                next_annotation=None
            )

        result = results[0]
        url_id = result[0]
        url = result[1]

        agency_suggestions = await self.get_agency_suggestions(session, url_id=url_id)

        # Get HTML content info
        html_content_infos = await self.get_html_content_info(url_id)
        response_html_info = convert_to_response_html_info(html_content_infos)

        return GetNextURLForAgencyAnnotationResponse(
            next_annotation=GetNextURLForAgencyAnnotationInnerResponse(
                url_id=url_id,
                url=url,
                html_info=response_html_info,
                agency_suggestions=agency_suggestions
            )
        )

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

        await session.commit()

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
    ) -> Optional[GetNextURLForFinalReviewResponse]:


        def annotations_exist_subquery(model: Type[Base]):
            return (
                select(
                    URL.id.label("url_id"),
                    case(
                        (
                            exists().where(URL.id == model.url_id), 1
                        ),
                        else_=0
                    ).label("exists")
                ).subquery()
            )

        def count_subquery(model: Type[Base]):
            return (
                select(
                    model.url_id,
                    func.count(model.url_id).label("count")
                ).group_by(model.url_id).subquery()
            )

        models = [
            AutoRelevantSuggestion,
            UserRelevantSuggestion,
            AutoRecordTypeSuggestion,
            UserRecordTypeSuggestion,
            AutomatedUrlAgencySuggestion,
            UserUrlAgencySuggestion
        ]

        exist_subqueries = [
            annotations_exist_subquery(model=model)
            for model in models
        ]

        sum_of_exist_subqueries = (
            sum(
                [
                    subquery.c.exists
                    for subquery in exist_subqueries]
            )
        )


        # Basic URL query
        url_query = (
            select(
                URL,
                (
                    sum_of_exist_subqueries
                ).label("total_distinct_annotation_count"),
            )
        )

        for subquery in exist_subqueries:
            url_query = url_query.outerjoin(
                subquery, URL.id == subquery.c.url_id
            )

        url_query = url_query.where(
                URL.outcome == URLStatus.PENDING.value
            )
        if batch_id is not None:
            url_query = url_query.where(
                URL.batch_id == batch_id
            )

        # The below relationships are joined directly to the URL
        single_join_relationships = [
            URL.html_content,
            URL.auto_record_type_suggestion,
            URL.auto_relevant_suggestion,
            URL.user_relevant_suggestion,
            URL.user_record_type_suggestion,
            URL.optional_data_source_metadata,
        ]

        options = [
            joinedload(relationship) for relationship in single_join_relationships
        ]

        # The below relationships are joined to entities that are joined to the URL
        double_join_relationships = [
            (URL.automated_agency_suggestions, AutomatedUrlAgencySuggestion.agency),
            (URL.user_agency_suggestion, UserUrlAgencySuggestion.agency),
            (URL.confirmed_agencies, ConfirmedURLAgency.agency)
        ]
        for primary, secondary in double_join_relationships:
            options.append(joinedload(primary).joinedload(secondary))

        # Apply options
        url_query = url_query.options(*options)

        # Apply order clause
        url_query = url_query.order_by(
            desc("total_distinct_annotation_count"),
            asc(URL.id)
        )

        # Apply limit
        url_query = url_query.limit(1)

        # Execute query
        raw_result = await session.execute(url_query)

        full_result = raw_result.unique().all()

        if len(full_result) == 0:
            return None
        result: URL = full_result[0][0]

        # Convert html content to response format
        html_content = result.html_content
        html_content_infos = [URLHTMLContentInfo(**html_info.__dict__) for html_info in html_content]

        if result.optional_data_source_metadata is None:
            optional_metadata = FinalReviewOptionalMetadata()
        else:
            optional_metadata = FinalReviewOptionalMetadata(
                record_formats=result.optional_data_source_metadata.record_formats,
                data_portal_type=result.optional_data_source_metadata.data_portal_type,
                supplying_entity=result.optional_data_source_metadata.supplying_entity
            )


        # Return
        return GetNextURLForFinalReviewResponse(
            id=result.id,
            url=result.url,
            html_info=convert_to_response_html_info(html_content_infos),
            name=result.name,
            description=result.description,
            annotations=FinalReviewAnnotationInfo(
                relevant=DTOConverter.final_review_annotation_relevant_info(
                    user_suggestion=result.user_relevant_suggestion,
                    auto_suggestion=result.auto_relevant_suggestion
                ),
                record_type=DTOConverter.final_review_annotation_record_type_info(
                    user_suggestion=result.user_record_type_suggestion,
                    auto_suggestion=result.auto_record_type_suggestion
                ),
                agency=DTOConverter.final_review_annotation_agency_info(
                    automated_agency_suggestions=result.automated_agency_suggestions,
                    user_agency_suggestion=result.user_agency_suggestion,
                    confirmed_agencies=result.confirmed_agencies
                )
            ),
            optional_metadata=optional_metadata
        )

    @session_manager
    async def approve_url(
            self,
            session: AsyncSession,
            approval_info: FinalReviewApprovalInfo,
            user_id: int,
    ) -> None:

        # Get URL
        def update_if_not_none(
                model,
                field,
                value: Optional[Any],
                required: bool=False
        ):
            if value is not None:
                setattr(model, field, value)
                return
            if not required:
                return
            model_value = getattr(model, field, None)
            if model_value is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Must specify {field} if it does not already exist"
                )


        query = (
            Select(URL)
            .where(URL.id == approval_info.url_id)
            .options(
                joinedload(URL.optional_data_source_metadata),
                joinedload(URL.confirmed_agencies),
            )
        )

        url = await session.execute(query)
        url = url.scalars().first()

        update_if_not_none(
            url,
            "record_type",
            approval_info.record_type.value if approval_info.record_type is not None else None,
            required=True
        )

        # Get existing agency ids
        existing_agencies = url.confirmed_agencies or []
        existing_agency_ids = [agency.agency_id for agency in existing_agencies]
        new_agency_ids = approval_info.agency_ids or []
        if len(existing_agency_ids) == 0 and len(new_agency_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must specify agency_id if URL does not already have a confirmed agency"
            )

        # Get any existing agency ids that are not in the new agency ids
        # If new agency ids are specified, overwrite existing
        if len(new_agency_ids) != 0:
            for existing_agency in existing_agencies:
                if existing_agency.id not in new_agency_ids:
                    # If the existing agency id is not in the new agency ids, delete it
                    await session.delete(existing_agency)
        # Add any new agency ids that are not in the existing agency ids
        for new_agency_id in new_agency_ids:
            if new_agency_id not in existing_agency_ids:
                # Check if the new agency exists in the database
                query = (
                    select(Agency)
                    .where(Agency.agency_id == new_agency_id)
                )
                existing_agency = await session.execute(query)
                existing_agency = existing_agency.scalars().first()
                if existing_agency is None:
                # If not, create it
                    agency = Agency(
                        agency_id=new_agency_id,
                        name=PLACEHOLDER_AGENCY_NAME,
                    )
                    session.add(agency)

                # If the new agency id is not in the existing agency ids, add it
                confirmed_url_agency = ConfirmedURLAgency(
                    url_id=approval_info.url_id,
                    agency_id=new_agency_id
                )
                session.add(confirmed_url_agency)

        # If it does, do nothing

        url.outcome = URLStatus.VALIDATED.value

        update_if_not_none(url, "name", approval_info.name, required=True)
        update_if_not_none(url, "description", approval_info.description, required=True)

        optional_metadata = url.optional_data_source_metadata
        if optional_metadata is None:
            url.optional_data_source_metadata = URLOptionalDataSourceMetadata(
                record_formats=approval_info.record_formats,
                data_portal_type=approval_info.data_portal_type,
                supplying_entity=approval_info.supplying_entity
            )
        else:
            update_if_not_none(
                optional_metadata,
                "record_formats",
                approval_info.record_formats
            )
            update_if_not_none(
                optional_metadata,
                "data_portal_type",
                approval_info.data_portal_type
            )
            update_if_not_none(
                optional_metadata,
                "supplying_entity",
                approval_info.supplying_entity
            )

        # Add approving user
        approving_user_url = ReviewingUserURL(
            user_id=user_id,
            url_id=approval_info.url_id
        )

        session.add(approving_user_url)

    @session_manager
    async def reject_url(
            self,
            session: AsyncSession,
            url_id: int,
            user_id: int
    ) -> None:

        query = (
            Select(URL)
            .where(URL.id == url_id)
        )

        url = await session.execute(query)
        url = url.scalars().first()

        url.outcome = URLStatus.NOT_RELEVANT.value

        # Add rejecting user
        rejecting_user_url = ReviewingUserURL(
            user_id=user_id,
            url_id=url_id
        )

        session.add(rejecting_user_url)

    @session_manager
    async def get_batch_by_id(self, session, batch_id: int) -> Optional[BatchInfo]:
        """Retrieve a batch by ID."""
        query = Select(Batch).where(Batch.id == batch_id)
        result = await session.execute(query)
        batch = result.scalars().first()
        return BatchInfo(**batch.__dict__)

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
            total_url_count=batch_info.total_url_count,
            original_url_count=batch_info.original_url_count,
            duplicate_url_count=batch_info.duplicate_url_count,
            compute_time=batch_info.compute_time,
            strategy_success_rate=batch_info.strategy_success_rate,
            metadata_success_rate=batch_info.metadata_success_rate,
            agency_match_rate=batch_info.agency_match_rate,
            record_type_match_rate=batch_info.record_type_match_rate,
            record_category_match_rate=batch_info.record_category_match_rate,
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
    async def get_recent_batch_status_info(
        self,
        session,
        page: int,
        collector_type: Optional[CollectorType] = None,
        status: Optional[BatchStatus] = None,
        has_pending_urls: Optional[bool] = None
    ) -> List[BatchInfo]:
        # Get only the batch_id, collector_type, status, and created_at
        limit = 100
        query = Select(Batch)
        if has_pending_urls is not None:
            pending_url_subquery = Select(URL).where(
                and_(
                    URL.batch_id == Batch.id,
                    URL.outcome == URLStatus.PENDING.value
                )
            )

            if has_pending_urls:
                # Query for all that have pending URLs
                query = query.where(exists(
                    pending_url_subquery
                ))
            else:
                # Query for all that DO NOT have pending URLs
                # (or that have no URLs at all)
                query = query.where(
                    not_(
                        exists(
                            pending_url_subquery
                        )
                    )
                )
        if collector_type:
            query = query.filter(Batch.strategy == collector_type.value)
        if status:
            query = query.filter(Batch.status == status.value)

        query = (query.
                 order_by(Batch.date_generated.desc()).
                 limit(limit).
                 offset((page - 1) * limit))
        raw_results = await session.execute(query)
        batches = raw_results.scalars().all()
        return [BatchInfo(**batch.__dict__) for batch in batches]

    @session_manager
    async def get_logs_by_batch_id(self, session, batch_id: int) -> List[LogOutputInfo]:
        query = Select(Log).filter_by(batch_id=batch_id).order_by(Log.created_at.asc())
        raw_results = await session.execute(query)
        logs = raw_results.scalars().all()
        return ([LogOutputInfo(**log.__dict__) for log in logs])

    @session_manager
    async def delete_old_logs(self, session):
        """
        Delete logs older than a day
        """
        statement = delete(Log).where(
            Log.created_at < datetime.now() - timedelta(days=1)
        )
        await session.execute(statement)

    async def get_agency_suggestions(self, session, url_id: int) -> List[GetNextURLForAgencyAgencyInfo]:
        # Get relevant autosuggestions and agency info, if an associated agency exists

        statement = (
            select(
                AutomatedUrlAgencySuggestion.agency_id,
                AutomatedUrlAgencySuggestion.is_unknown,
                Agency.name,
                Agency.state,
                Agency.county,
                Agency.locality
            )
            .join(Agency, isouter=True)
            .where(AutomatedUrlAgencySuggestion.url_id == url_id)
        )
        raw_autosuggestions = await session.execute(statement)
        autosuggestions = raw_autosuggestions.all()
        agency_suggestions = []
        for autosuggestion in autosuggestions:
            agency_id = autosuggestion[0]
            is_unknown = autosuggestion[1]
            name = autosuggestion[2]
            state = autosuggestion[3]
            county = autosuggestion[4]
            locality = autosuggestion[5]
            agency_suggestions.append(GetNextURLForAgencyAgencyInfo(
                suggestion_type=SuggestionType.AUTO_SUGGESTION if not is_unknown else SuggestionType.UNKNOWN,
                pdap_agency_id=agency_id,
                agency_name=name,
                state=state,
                county=county,
                locality=locality
            ))
        return agency_suggestions

    @session_manager
    async def get_next_url_for_all_annotations(self, session, batch_id: Optional[int] = None) -> GetNextURLForAllAnnotationResponse:
        query = (
            Select(URL)
            .where(
                and_(
                    URL.outcome == URLStatus.PENDING.value,
                    StatementComposer.user_suggestion_not_exists(UserUrlAgencySuggestion),
                    StatementComposer.user_suggestion_not_exists(UserRecordTypeSuggestion),
                    StatementComposer.user_suggestion_not_exists(UserRelevantSuggestion),
                )
            )
        )
        if batch_id is not None:
            query = query.where(URL.batch_id == batch_id)

        load_options = [
            URL.html_content,
            URL.automated_agency_suggestions,
            URL.auto_relevant_suggestion,
            URL.auto_record_type_suggestion
        ]
        select_in_loads = [selectinload(load_option) for load_option in load_options]

        # Add load options
        query = query.options(
            *select_in_loads
        )

        query = query.order_by(URL.id.asc()).limit(1)
        raw_results = await session.execute(query)
        url = raw_results.scalars().one_or_none()
        if url is None:
            return GetNextURLForAllAnnotationResponse(
                next_annotation=None
            )

        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        if url.auto_relevant_suggestion is not None:
            auto_relevant = url.auto_relevant_suggestion.relevant
        else:
            auto_relevant = None

        if url.auto_record_type_suggestion is not None:
            auto_record_type = url.auto_record_type_suggestion.record_type
        else:
            auto_record_type = None

        agency_suggestions = await self.get_agency_suggestions(session, url_id=url.id)

        return GetNextURLForAllAnnotationResponse(
            next_annotation=GetNextURLForAllAnnotationInnerResponse(
                url_id=url.id,
                url=url.url,
                html_info=html_response_info,
                suggested_relevant=auto_relevant,
                suggested_record_type=auto_record_type,
                agency_suggestions=agency_suggestions
            )
        )

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
            relevant=post_info.is_relevant
        )
        session.add(relevant_suggestion)

        # If not relevant, do nothing else
        if not post_info.is_relevant:
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
                    (Batch.status == status.value,
                    Batch.id)
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
                    (URL.outcome == status.value,
                    URL.id)
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
                    (URL.outcome == status.value,
                    URL.id)
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
                    (URL.outcome == status.value,
                    URL.id)
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
                func.count(case(
                    (flags.c.has_user_record_type_annotation == True, 1))
                ).label('user_record_type_count'),
                func.count(case(
                    (flags.c.has_user_relevant_annotation == True, 1))
                ).label('user_relevant_count'),
                func.count(case(
                    (flags.c.has_user_agency_annotation == True, 1))
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


    @session_manager
    async def mark_all_as_duplicates(self, session: AsyncSession, url_ids: List[int]):
        query = update(URL).where(URL.id.in_(url_ids)).values(outcome=URLStatus.DUPLICATE.value)
        await session.execute(query)

    @session_manager
    async def mark_all_as_404(self, session: AsyncSession, url_ids: List[int]):
        query = update(URL).where(URL.id.in_(url_ids)).values(outcome=URLStatus.NOT_FOUND.value)
        await session.execute(query)

    @session_manager
    async def mark_all_as_recently_probed_for_404(
        self,
        session: AsyncSession,
        url_ids: List[int],
        dt: datetime = func.now()
    ):
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        values = [
            {"url_id": url_id, "last_probed_at": dt} for url_id in url_ids
        ]
        stmt = pg_insert(URLProbedFor404).values(values)
        update_stmt = stmt.on_conflict_do_update(
            index_elements=['url_id'],
            set_={"last_probed_at": dt}
        )
        await session.execute(update_stmt)


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