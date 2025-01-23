from functools import wraps

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOs.MetadataAnnotationInfo import MetadataAnnotationInfo
from collector_db.DTOs.URLAnnotationInfo import URLAnnotationInfo
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import URLMetadata, URL, URLErrorInfo, URLHTMLContent, Base, MetadataAnnotation, \
    RootURL
from collector_manager.enums import URLStatus
from core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo, GetURLsResponseMetadataInfo, GetURLsResponseErrorInfo, \
    GetURLsResponseInnerInfo
from core.DTOs.RelevanceAnnotationInfo import RelevanceAnnotationPostInfo

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
        url_metadata = URLMetadata(**url_metadata_info.model_dump())
        session.add(url_metadata)

    @session_manager
    async def add_url_metadatas(self, session: AsyncSession, url_metadata_infos: list[URLMetadataInfo]):
        for url_metadata_info in url_metadata_infos:
            url_metadata = URLMetadata(**url_metadata_info.model_dump())
            session.add(url_metadata)

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
        statement = (select(URL, URLErrorInfo.error, URLErrorInfo.updated_at)
                     .join(URLErrorInfo)
                     .where(URL.outcome == URLStatus.ERROR.value)
                     .order_by(URL.id))
        scalar_result = await session.execute(statement)
        results = scalar_result.all()
        final_results = []
        for url, error, updated_at in results:
            final_results.append(URLErrorPydanticInfo(url_id=url.id, error=error, updated_at=updated_at))

        return final_results

    @session_manager
    async def add_html_content_infos(self, session: AsyncSession, html_content_infos: list[URLHTMLContentInfo]):
        for html_content_info in html_content_infos:
            # Add HTML Content Info to database
            db_html_content_info = URLHTMLContent(**html_content_info.model_dump())
            session.add(db_html_content_info)

    @session_manager
    async def get_pending_urls_without_html_data(self, session: AsyncSession):
        # TODO: Add test that includes some urls WITH html data. Check they're not returned
        statement = (select(URL).
                     outerjoin(URLHTMLContent).
                     where(URLHTMLContent.id == None).
                     where(URL.outcome == URLStatus.PENDING.value).
                     limit(100).
                     order_by(URL.id))
        scalar_result = await session.scalars(statement)
        return scalar_result.all()

    @session_manager
    async def get_urls_with_html_data_and_no_relevancy_metadata(
            self,
            session: AsyncSession
    ) -> list[URLWithHTML]:
        # Get URLs with no relevancy metadata
        statement = (select(URL.id, URL.url, URLHTMLContent).
                     join(URLHTMLContent).
                     where(URL.outcome == URLStatus.PENDING.value)
                    # No relevancy metadata
                    .where(
                        ~exists(
                            select(URLMetadata.id).
                            where(
                                URLMetadata.url_id == URL.id,
                                URLMetadata.attribute == URLMetadataAttributeType.RELEVANT.value
                            )
                        )
                    )
                    .limit(100)
                    .order_by(URL.id)
        )
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
    async def get_next_url_for_relevance_annotation(
            self,
            session: AsyncSession,
            user_id: int
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
            )
            .join(URLMetadata)
            # Metadata must be relevant
            .where(URLMetadata.attribute == URLMetadataAttributeType.RELEVANT.value)
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
            html_infos=[]
        )
        for _, _, content_type, content in result:
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
            annotation_info: RelevanceAnnotationPostInfo):
        annotation = MetadataAnnotation(
            metadata_id=metadata_id,
            user_id=user_id,
            value=str(annotation_info.is_relevant)
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



