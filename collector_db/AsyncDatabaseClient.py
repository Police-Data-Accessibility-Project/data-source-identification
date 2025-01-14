from functools import wraps

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import URLMetadata, URL, URLErrorInfo
from collector_manager.enums import URLStatus


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
    async def get_url_metadata_by_status(self, session: AsyncSession, url_status: URLStatus):
        statement = select(URLMetadata).join(URL).where(URL.outcome == url_status.value)
        scalar_result = await session.scalars(statement)
        model_result = scalar_result.all()
        return [URLMetadataInfo(**url_metadata.__dict__) for url_metadata in model_result]

    @session_manager
    async def add_url_metadata(self, session: AsyncSession, url_metadata_info: URLMetadataInfo):
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
        statement = select(URL, URLErrorInfo.error, URLErrorInfo.updated_at).join(URLErrorInfo).where(URL.outcome == URLStatus.ERROR.value)
        scalar_result = await session.execute(statement)
        results = scalar_result.all()
        final_results = []
        for url, error, updated_at in results:
            final_results.append(URLErrorPydanticInfo(url_id=url.id, error=error, updated_at=updated_at))

        return final_results


