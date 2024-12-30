from functools import wraps

from sqlalchemy import create_engine, Row, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from typing import Optional, List

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInfo, DuplicateInsertInfo
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.helper_functions import get_postgres_connection_string
from collector_db.models import Base, Batch, URL, Log, Duplicate
from collector_manager.enums import CollectorType
from core.DTOs.BatchStatusInfo import BatchStatusInfo
from core.enums import BatchStatus



# SQLAlchemy ORM models


# Database Client
class DatabaseClient:
    def __init__(self, db_url: str = get_postgres_connection_string()):
        """Initialize the DatabaseClient."""
        self.engine: AsyncEngine = create_async_engine(
            url=db_url,
            echo=ConfigManager.get_sqlalchemy_echo(),
        )
        self.session_maker = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )
        self.session = None

    async def init_db(self):
        """Initialize the database schema (create tables)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def session_manager(method):
        @wraps(method)
        async def wrapper(self, *args, **kwargs):
            async with self.session_maker() as session:
                try:
                    result = await method(self, session, *args, **kwargs)
                    session.commit()
                    return result
                except Exception as e:
                    session.rollback()
                    raise e

        return wrapper

    def row_to_dict(self, row: Row) -> dict:
        return dict(row._mapping)


    @session_manager
    async def insert_batch(self, session, batch_info: BatchInfo) -> int:
        """Insert a new batch into the database and return its ID."""
        batch = Batch(
            strategy=batch_info.strategy,
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
        session.add(batch)
        await session.flush()
        return batch.id

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
        batch = await session.get(Batch, batch_id).scalar()
        batch.total_url_count = total_url_count
        batch.original_url_count = original_url_count
        batch.duplicate_url_count = duplicate_url_count
        batch.status = batch_status.value
        batch.compute_time = compute_time

    @session_manager
    async def get_batch_by_id(self, session, batch_id: int) -> Optional[BatchInfo]:
        """Retrieve a batch by ID."""
        query = await session.execute(select(Batch).filter_by(id=batch_id))
        batch = query.scalar_one_or_none()
        return BatchInfo(**batch.__dict__) if batch else None

    async def insert_urls(self, url_infos: List[URLInfo], batch_id: int) -> InsertURLsInfo:
        url_mappings = []
        duplicates = []
        for url_info in url_infos:
            url_info.batch_id = batch_id
            try:
                url_id = await self.insert_url(url_info)
                url_mappings.append(URLMapping(url_id=url_id, url=url_info.url))
            except IntegrityError:
                orig_url_info = self.get_url_info_by_url(url_info.url)
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
        )

    @session_manager
    async def insert_duplicates(self, session, duplicate_infos: list[DuplicateInsertInfo]):
        for duplicate_info in duplicate_infos:
            duplicate = Duplicate(
                batch_id=duplicate_info.duplicate_batch_id,
                original_url_id=duplicate_info.original_url_id,
            )
            session.add(duplicate)



    @session_manager
    async def get_url_info_by_url(self, session, url: str) -> Optional[URLInfo]:
        url = await session.execute(select(URL).filter_by(url=url)).scalar_one_or_none()
        return URLInfo(**url.__dict__) if url else None

    @session_manager
    async def insert_url(self, session, url_info: URLInfo) -> int:
        """Insert a new URL into the database."""
        url_entry = URL(
            batch_id=url_info.batch_id,
            url=url_info.url,
            url_metadata=url_info.url_metadata,
            outcome=url_info.outcome.value
        )
        session.add(url_entry)
        await session.flush()
        return url_entry.id


    @session_manager
    async def get_urls_by_batch(self, session, batch_id: int) -> List[URLInfo]:
        """Retrieve all URLs associated with a batch."""
        query = await session.execute(select(URL).filter_by(batch_id=batch_id))
        urls = query.scalars().all()
        return ([URLInfo(**url.__dict__) for url in urls])

    @session_manager
    async def is_duplicate_url(self, session, url: str) -> bool:
        result = await session.execute(select(URL).filter_by(url=url)).scalar_one_or_none()
        return result is not None

    @session_manager
    async def insert_logs(self, session, log_infos: List[LogInfo]):
        for log_info in log_infos:
            log = Log(log=log_info.log, batch_id=log_info.batch_id)
            session.add(log)

    @session_manager
    async def get_logs_by_batch_id(self, session, batch_id: int) -> List[LogInfo]:
        query = await session.execute(select(Log).filter_by(batch_id=batch_id))
        logs = query.scalars().all()
        return [LogInfo(**log.__dict__) for log in logs]

    @session_manager
    async def get_all_logs(self, session) -> List[LogInfo]:
        query = await session.execute(select(Log))
        logs = query.scalars().all()
        return [LogInfo(**log.__dict__) for log in logs]


    @session_manager
    async def add_duplicate_info(self, session, duplicate_infos: list[DuplicateInfo]):
        # TODO: Add test for this method when testing CollectorDatabaseProcessor
        for duplicate_info in duplicate_infos:
            duplicate = Duplicate(
                batch_id=duplicate_info.duplicate_batch_id,
                original_url_id=duplicate_info.original_url_id,
            )
            session.add(duplicate)

    @session_manager
    async def get_batch_status(self, session, batch_id: int) -> BatchStatus:
        query = await session.execute(select(Batch).filter_by(id=batch_id))
        batch = query.scalar_one_or_none()
        return BatchStatus(batch.status)

    @session_manager
    async def get_recent_batch_status_info(
        self,
        session,
        limit: int,
        collector_type: Optional[CollectorType] = None,
        status: Optional[BatchStatus] = None,
    ) -> List[BatchStatusInfo]:
        # Get only the batch_id, collector_type, status, and created_at
        query = ((select(Batch.id, Batch.collector_type, Batch.status, Batch.created_at)
                 .order_by(Batch.created_at.desc()))
                 .limit(limit))
        if collector_type:
            query = query.filter(Batch.collector_type == collector_type.value)
        if status:
            query = query.filter(Batch.status == status.value)
        results = await session.execute(query)
        return [
            BatchStatusInfo(
                id=result.id,
                strategy=result.collector_type,
                status=result.status,
                date_generated=result.created_at,
            )
            for result in results
        ]

    @session_manager
    async def get_duplicates_by_batch_id(self, session, batch_id: int) -> List[DuplicateInfo]:
        original_batch = aliased(Batch)
        duplicate_batch = aliased(Batch)

        query = (
            select(
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
        )

        results = await session.execute(query)
        rows = results.fetchall()

        final_results = [
            DuplicateInfo(
                source_url=row.source_url,
                duplicate_batch_id=row.duplicate_batch_id,
                duplicate_metadata=row.duplicate_batch_parameters,
                original_batch_id=row.original_batch_id,
                original_metadata=row.original_batch_parameters,
                original_url_id=row.original_url_id,
            )
            for row in rows
        ]

        return final_results

    @session_manager
    async def delete_all_logs(self, session):
        await session.execute(delete(Log))

if __name__ == "__main__":
    client = DatabaseClient()
    print("Database client initialized.")
