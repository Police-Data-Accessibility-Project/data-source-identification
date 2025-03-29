from functools import wraps
from typing import Optional, Type, Any

from fastapi import HTTPException
from sqlalchemy import select, exists, func, case, desc, Select, not_, and_, or_, update, Delete, Insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload, joinedload, QueryableAttribute
from sqlalchemy.sql.functions import coalesce
from starlette import status

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOConverter import DTOConverter
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.StatementComposer import StatementComposer
from collector_db.constants import PLACEHOLDER_AGENCY_NAME
from collector_db.enums import URLMetadataAttributeType, TaskType
from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import URL, URLErrorInfo, URLHTMLContent, Base, \
    RootURL, Task, TaskError, LinkTaskURL, Batch, Agency, AutomatedUrlAgencySuggestion, \
    UserUrlAgencySuggestion, AutoRelevantSuggestion, AutoRecordTypeSuggestion, UserRelevantSuggestion, \
    UserRecordTypeSuggestion, ApprovingUserURL, URLOptionalDataSourceMetadata, ConfirmedURLAgency
from collector_manager.enums import URLStatus, CollectorType
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    GetNextURLForAgencyAgencyInfo, GetNextURLForAgencyAnnotationInnerResponse
from core.DTOs.GetNextURLForFinalReviewResponse import GetNextURLForFinalReviewResponse, FinalReviewAnnotationInfo, \
    FinalReviewOptionalMetadata
from core.DTOs.GetTasksResponse import GetTasksResponse, GetTasksResponseTaskInfo
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo, GetURLsResponseErrorInfo, \
    GetURLsResponseInnerInfo
from core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from core.DTOs.task_data_objects.AgencyIdentificationTDO import AgencyIdentificationTDO
from core.DTOs.task_data_objects.URLMiscellaneousMetadataTDO import URLMiscellaneousMetadataTDO
from core.enums import BatchStatus, SuggestionType, RecordType
from html_tag_collector.DataClassTags import convert_to_response_html_info

# Type Hints

UserSuggestionModel = UserRelevantSuggestion or UserRecordTypeSuggestion or UserUrlAgencySuggestion
AutoSuggestionModel = AutoRelevantSuggestion or AutoRecordTypeSuggestion or AutomatedUrlAgencySuggestion


def add_standard_limit_and_offset(statement, page, limit=100):
    offset = (page - 1) * limit
    return statement.limit(limit).offset(offset)


class AsyncDatabaseClient:
    def __init__(self, db_url: str = get_postgres_connection_string(is_async=True)):
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
            user_id: int
    ) -> URL:
        url_query = (
            select(
                URL,
            )
            .where(exists(select(URLHTMLContent).where(URLHTMLContent.url_id == URL.id)))
            # URL must not have metadata annotation by this user
            .where(
                not_(
                    exists(
                        select(user_suggestion_model_to_exclude)
                        .where(
                            user_suggestion_model_to_exclude.url_id == URL.id,
                            user_suggestion_model_to_exclude.user_id == user_id
                        )
                    )
                )
            ).options(
                joinedload(auto_suggestion_relationship),
                joinedload(URL.html_content)
            ).
            limit(1)
        )

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
            user_id: int
    ) -> Optional[GetNextRelevanceAnnotationResponseInfo]:

        url = await self.get_next_url_for_user_annotation(
            session,
            user_suggestion_model_to_exclude=UserRelevantSuggestion,
            auto_suggestion_relationship=URL.auto_relevant_suggestion,
            user_id=user_id
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
            user_id: int
    ) -> Optional[GetNextRecordTypeAnnotationResponseInfo]:

        url = await self.get_next_url_for_user_annotation(
            session,
            user_suggestion_model_to_exclude=UserRecordTypeSuggestion,
            auto_suggestion_relationship=URL.auto_record_type_suggestion,
            user_id=user_id
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
            ).limit(100).order_by(URL.id)
        )

        scalar_result = await session.scalars(query)
        all_results = scalar_result.all()
        final_results = []
        for result in all_results:
            tdo = URLMiscellaneousMetadataTDO(
                url_id=result.id,
                collector_metadata=result.collector_metadata,
                collector_type=CollectorType(result.batch.strategy),
            )
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
    async def get_pending_urls_without_html_data(self, session: AsyncSession):
        # TODO: Add test that includes some urls WITH html data. Check they're not returned
        statement = self.statement_composer.pending_urls_without_html_data()
        statement = statement.limit(100).order_by(URL.id)
        scalar_result = await session.scalars(statement)
        return scalar_result.all()

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
        )
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
            self, session: AsyncSession, user_id: int
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
                and_(
                    URL.outcome == URLStatus.PENDING.value
                )
            )
            # Must not have been annotated by this user
            .join(UserUrlAgencySuggestion, isouter=True)
            .where(
                ~exists(
                    select(UserUrlAgencySuggestion).
                    where(
                        (UserUrlAgencySuggestion.user_id == user_id) &
                        (UserUrlAgencySuggestion.url_id == URL.id)
                    ).
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
            session: AsyncSession
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

        count_subqueries = [
            count_subquery(model=model)
            for model in models
        ]

        sum_of_count_subqueries = (
            sum(
                [
                    coalesce(subquery.c.count, 0)
                    for subquery in count_subqueries
                ]
            )
        )

        # Basic URL query
        url_query = (
            select(
                URL,
                (
                    sum_of_exist_subqueries
                ).label("total_distinct_annotation_count"),
                (
                    sum_of_count_subqueries
                ).label("total_overall_annotation_count")
            )
        )

        for subquery in (exist_subqueries + count_subqueries):
            url_query = url_query.outerjoin(
                subquery, URL.id == subquery.c.url_id
            )

        url_query = url_query.where(
                URL.outcome == URLStatus.PENDING.value
            )

        # The below relationships are joined directly to the URL
        single_join_relationships = [
            URL.html_content,
            URL.auto_record_type_suggestion,
            URL.auto_relevant_suggestion,
            URL.user_relevant_suggestions,
            URL.user_record_type_suggestions,
            URL.optional_data_source_metadata,
        ]

        options = [
            joinedload(relationship) for relationship in single_join_relationships
        ]

        # The below relationships are joined to entities that are joined to the URL
        double_join_relationships = [
            (URL.automated_agency_suggestions, AutomatedUrlAgencySuggestion.agency),
            (URL.user_agency_suggestions, UserUrlAgencySuggestion.agency),
            (URL.confirmed_agencies, ConfirmedURLAgency.agency)
        ]
        for primary, secondary in double_join_relationships:
            options.append(joinedload(primary).joinedload(secondary))

        # Apply options
        url_query = url_query.options(*options)

        # Apply order clause
        url_query = url_query.order_by(
            desc("total_distinct_annotation_count"),
            desc("total_overall_annotation_count"),
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
                    user_suggestions=result.user_relevant_suggestions,
                    auto_suggestion=result.auto_relevant_suggestion
                ),
                record_type=DTOConverter.final_review_annotation_record_type_info(
                    user_suggestions=result.user_record_type_suggestions,
                    auto_suggestion=result.auto_record_type_suggestion
                ),
                agency=DTOConverter.final_review_annotation_agency_info(
                    automated_agency_suggestions=result.automated_agency_suggestions,
                    user_agency_suggestions=result.user_agency_suggestions,
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
        update_if_not_none(
            url,
            "relevant",
            approval_info.relevant,
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

        approving_user_url = ApprovingUserURL(
            user_id=user_id,
            url_id=approval_info.url_id
        )

        session.add(approving_user_url)
