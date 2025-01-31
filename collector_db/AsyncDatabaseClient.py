from functools import wraps
from typing import Optional

from sqlalchemy import select, exists, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOs.MetadataAnnotationInfo import MetadataAnnotationInfo
from collector_db.DTOs.TaskInfo import TaskInfo
from collector_db.DTOs.URLAnnotationInfo import URLAnnotationInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.StatementComposer import StatementComposer
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource, TaskType
from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import URLMetadata, URL, URLErrorInfo, URLHTMLContent, Base, MetadataAnnotation, \
    RootURL, Task, TaskError, LinkTaskURL
from collector_manager.enums import URLStatus
from core.DTOs.GetTasksResponse import GetTasksResponse, GetTasksResponseTaskInfo
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo, GetURLsResponseMetadataInfo, GetURLsResponseErrorInfo, \
    GetURLsResponseInnerInfo
from core.DTOs.RelevanceAnnotationPostInfo import RelevanceAnnotationPostInfo
from core.enums import BatchStatus


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
    def _add_models(session: AsyncSession, model_class, models):
        for model in models:
            instance = model_class(**model.model_dump())
            session.add(instance)


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
    async def get_url_metadata_by_status(
            self,
            session: AsyncSession,
            url_status: URLStatus,
            offset: int = 0
    ):
        statement = (select(URLMetadata)
                     .join(URL)
                     .where(URL.outcome == url_status.value)
                     .limit(100)
                     .offset(offset)
                     .order_by(URLMetadata.id))
        scalar_result = await session.scalars(statement)
        model_result = scalar_result.all()
        return [URLMetadataInfo(**url_metadata.__dict__) for url_metadata in model_result]

    @session_manager
    async def add_url_metadata(self, session: AsyncSession, url_metadata_info: URLMetadataInfo):
        self._add_models(session, URLMetadata, [url_metadata_info])

    @session_manager
    async def add_url_metadatas(self, session: AsyncSession, url_metadata_infos: list[URLMetadataInfo]):
        self._add_models(session, URLMetadata, url_metadata_infos)

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
        self._add_models(session, URLHTMLContent, html_content_infos)

    @session_manager
    async def has_pending_urls_without_html_data(self, session: AsyncSession) -> bool:
        statement = self.statement_composer.pending_urls_without_html_data()
        statement = statement.limit(1)
        scalar_result = await session.scalars(statement)
        return bool(scalar_result.first())

    @session_manager
    async def get_pending_urls_without_html_data(self, session: AsyncSession):
        # TODO: Add test that includes some urls WITH html data. Check they're not returned
        statement = self.statement_composer.pending_urls_without_html_data()
        statement = statement.limit(100).order_by(URL.id)
        scalar_result = await session.scalars(statement)
        return scalar_result.all()

    @session_manager
    async def get_urls_with_html_data_and_without_metadata_type(
            self,
            session: AsyncSession,
            without_metadata_type: URLMetadataAttributeType = URLMetadataAttributeType.RELEVANT
    ) -> list[URLWithHTML]:

        # Get URLs with no relevancy metadata
        statement = (select(URL.id, URL.url, URLHTMLContent).
                     join(URLHTMLContent).
                     where(URL.outcome == URLStatus.PENDING.value))
        statement = self.statement_composer.exclude_urls_with_select_metadata(
            statement=statement,
            attribute=without_metadata_type
        )
        statement = statement.limit(100).order_by(URL.id)
        raw_result = await session.execute(statement)
        result = raw_result.all()
        url_ids_to_urls = {url_id: url for url_id, url, _ in result}
        url_ids_to_html_info = {url_id: [] for url_id, _, _ in result}

        for url_id, _, html_info in result:
            url_ids_to_html_info[url_id].append(
                URLHTMLContentInfo(**html_info.__dict__)
            )

        final_results = []
        for url_id, url in url_ids_to_urls.items():
            url_with_html = URLWithHTML(
                url_id=url_id,
                url=url,
                html_infos=url_ids_to_html_info[url_id]
            )
            final_results.append(url_with_html)


        return final_results

    @session_manager
    async def has_pending_urls_with_html_data_and_without_metadata_type(
        self,
        session: AsyncSession,
        without_metadata_type: URLMetadataAttributeType = URLMetadataAttributeType.RELEVANT
    ) -> bool:
        # TODO: Generalize this so that it can exclude based on other attributes
        # Get URLs with no relevancy metadata
        statement = (select(URL.id, URL.url, URLHTMLContent).
                     join(URLHTMLContent).
                     where(URL.outcome == URLStatus.PENDING.value))
        statement = self.statement_composer.exclude_urls_with_select_metadata(
            statement=statement,
            attribute=without_metadata_type
        )
        statement = statement.limit(1)
        raw_result = await session.execute(statement)
        result = raw_result.all()
        return len(result) > 0

    @session_manager
    async def get_urls_with_metadata(
            self,
            session: AsyncSession,
            attribute: URLMetadataAttributeType,
            validation_status: ValidationStatus,
            offset: int = 0
    ) -> list[URLMetadataInfo]:
        statement = (select(URL.id, URLMetadata.id).
                     join(URLMetadata).
                     where(URLMetadata.attribute == attribute.value).
                     where(URLMetadata.validation_status == validation_status.value).
                     limit(100).
                     offset(offset).
                     order_by(URL.id)
                     )

        raw_result = await session.execute(statement)
        result = raw_result.all()
        final_results = []
        for url_id, url_metadata_id in result:
            info = URLMetadataInfo(
                url_id=url_id,
                id=url_metadata_id,
            )
            final_results.append(info)

        return final_results

    @session_manager
    async def update_url_metadata_status(self, session: AsyncSession, metadata_ids: list[int], validation_status: ValidationStatus):
        for metadata_id in metadata_ids:
            statement = select(URLMetadata).where(URLMetadata.id == metadata_id)
            scalar_result = await session.scalars(statement)
            url_metadata = scalar_result.first()
            url_metadata.validation_status = validation_status

    @session_manager
    async def get_next_url_for_annotation(
            self,
            session: AsyncSession,
            user_id: int,
            metadata_type: URLMetadataAttributeType
    ) -> URLAnnotationInfo:
        # Get a URL, its relevancy metadata ID, and HTML data
        # For a URL which has not yet been annotated by this user id
        # First, subquery retrieving URL and its metadata ID where its relevant metadata
        #  does not have an annotation for that user
        subquery = (
            select(
                URL.id.label("url_id"),
                URL.url,
                URLMetadata.id.label("metadata_id"),
                URLMetadata.value,
            )
            .join(URLMetadata)
            # Metadata must be relevant
            .where(URLMetadata.attribute == metadata_type.value)
            # Metadata must not be validated
            .where(URLMetadata.validation_status == ValidationStatus.PENDING_VALIDATION.value)
            # URL must have HTML content entries
            .where(exists(select(URLHTMLContent).where(URLHTMLContent.url_id == URL.id)))
            # URL must not have been annotated by the user
            .where(~exists(
                select(MetadataAnnotation).
                where(
                    MetadataAnnotation.metadata_id == URLMetadata.id,
                    MetadataAnnotation.user_id == user_id
                )
            ))
            .limit(1)
        )

        raw_result = await session.execute(subquery)
        result = raw_result.all()

        # Next, get all HTML content for the URL

        statement = (
            select(
                subquery.c.url,
                subquery.c.metadata_id,
                subquery.c.value,
                URLHTMLContent.content_type,
                URLHTMLContent.content,
            )
            .join(URLHTMLContent)
            .where(subquery.c.url_id == URLHTMLContent.url_id)
        )

        raw_result = await session.execute(statement)
        result = raw_result.all()

        if len(result) == 0:
            # No available URLs to annotate
            return None

        annotation_info = URLAnnotationInfo(
            url=result[0][0],
            metadata_id=result[0][1],
            suggested_value=result[0][2],
            html_infos=[]
        )
        for _, _, _, content_type, content in result:
            html_info = URLHTMLContentInfo(
                content_type=content_type,
                content=content
            )
            annotation_info.html_infos.append(html_info)
        return annotation_info

    @session_manager
    async def add_relevance_annotation(
            self,
            session: AsyncSession,
            user_id: int,
            metadata_id: int,
            annotation: str
    ):
        annotation = MetadataAnnotation(
            metadata_id=metadata_id,
            user_id=user_id,
            value=annotation
        )
        session.add(annotation)

    @session_manager
    async def get_annotations_for_metadata_id(
            self,
            session: AsyncSession,
            metadata_id: int
    ) -> list[MetadataAnnotation]:
        statement = (select(MetadataAnnotation).
                     where(MetadataAnnotation.metadata_id == metadata_id))
        scalar_result = await session.scalars(statement)
        all_results = scalar_result.all()
        return [MetadataAnnotationInfo(**result.__dict__) for result in all_results]

    @session_manager
    async def get_all(self, session, model: Base):
        """
        Get all records of a model
        Used primarily in testing
        """
        statement = select(model)
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
            selectinload(URL.url_metadata), selectinload(URL.error_info)
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
            metadata_results = []
            for metadata in result.url_metadata:
                metadata_result = GetURLsResponseMetadataInfo(
                    id=metadata.id,
                    attribute=URLMetadataAttributeType(metadata.attribute),
                    value=metadata.value,
                    validation_status=ValidationStatus(metadata.validation_status),
                    validation_source=ValidationSource(metadata.validation_source),
                    created_at=metadata.created_at,
                    updated_at=metadata.updated_at
                )
                metadata_results.append(metadata_result)
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
                    metadata=metadata_results
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
