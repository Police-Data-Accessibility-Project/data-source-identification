from functools import wraps

from sqlalchemy import create_engine, Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import Optional, List

from collector_db.ConfigManager import ConfigManager
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInfo
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
        self.engine = create_engine(
            url=db_url,
            echo=ConfigManager.get_sqlalchemy_echo(),
        )
        Base.metadata.create_all(self.engine)
        self.session_maker = scoped_session(sessionmaker(bind=self.engine))
        self.session = None

    def session_manager(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            session = self.session_maker()
            try:
                result = method(self, session, *args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()  # Ensures the session is cleaned up

        return wrapper

    def row_to_dict(self, row: Row) -> dict:
        return dict(row._mapping)


    @session_manager
    def insert_batch(self, session, batch_info: BatchInfo) -> int:
        """Insert a new batch into the database and return its ID."""
        batch = Batch(
            strategy=batch_info.strategy,
            status=batch_info.status.value,
            parameters=batch_info.parameters,
            count=batch_info.count,
            compute_time=batch_info.compute_time,
            strategy_success_rate=batch_info.strategy_success_rate,
            metadata_success_rate=batch_info.metadata_success_rate,
            agency_match_rate=batch_info.agency_match_rate,
            record_type_match_rate=batch_info.record_type_match_rate,
            record_category_match_rate=batch_info.record_category_match_rate,
        )
        session.add(batch)
        session.commit()
        session.refresh(batch)
        return batch.id

    @session_manager
    def update_batch_post_collection(
        self,
        session,
        batch_id: int,
        url_count: int,
        batch_status: BatchStatus,
        compute_time: float = None,
    ):
        batch = session.query(Batch).filter_by(id=batch_id).first()
        batch.count = url_count
        batch.status = batch_status.value
        batch.compute_time = compute_time

    @session_manager
    def get_batch_by_id(self, session, batch_id: int) -> Optional[BatchInfo]:
        """Retrieve a batch by ID."""
        batch = session.query(Batch).filter_by(id=batch_id).first()
        return BatchInfo(**batch.__dict__)

    def insert_urls(self, url_infos: List[URLInfo], batch_id: int) -> InsertURLsInfo:
        url_mappings = []
        duplicates = []
        for url_info in url_infos:
            url_info.batch_id = batch_id
            try:
                url_id = self.insert_url(url_info)
                url_mappings.append(URLMapping(url_id=url_id, url=url_info.url))
            except IntegrityError:
                orig_url_info = self.get_url_info_by_url(url_info.url)
                duplicates.append(DuplicateInfo(
                    source_url=url_info.url,
                    original_url_id=orig_url_info.id,
                    duplicate_metadata=url_info.url_metadata,
                    original_metadata=orig_url_info.url_metadata
                ))

        return InsertURLsInfo(url_mappings=url_mappings, duplicates=duplicates)


    @session_manager
    def get_url_info_by_url(self, session, url: str) -> Optional[URLInfo]:
        url = session.query(URL).filter_by(url=url).first()
        return URLInfo(**url.__dict__)

    @session_manager
    def insert_url(self, session, url_info: URLInfo) -> int:
        """Insert a new URL into the database."""
        url_entry = URL(
            batch_id=url_info.batch_id,
            url=url_info.url,
            url_metadata=url_info.url_metadata,
            outcome=url_info.outcome.value
        )
        session.add(url_entry)
        session.commit()
        session.refresh(url_entry)
        return url_entry.id


    @session_manager
    def get_urls_by_batch(self, session, batch_id: int) -> List[URLInfo]:
        """Retrieve all URLs associated with a batch."""
        urls = session.query(URL).filter_by(batch_id=batch_id).all()
        return ([URLInfo(**url.__dict__) for url in urls])

    @session_manager
    def is_duplicate_url(self, session, url: str) -> bool:
        result = session.query(URL).filter_by(url=url).first()
        return result is not None

    @session_manager
    def insert_logs(self, session, log_infos: List[LogInfo]):
        for log_info in log_infos:
            log = Log(log=log_info.log, batch_id=log_info.batch_id)
            session.add(log)

    @session_manager
    def get_logs_by_batch_id(self, session, batch_id: int) -> List[LogInfo]:
        logs = session.query(Log).filter_by(batch_id=batch_id).all()
        return ([LogInfo(**log.__dict__) for log in logs])

    @session_manager
    def get_all_logs(self, session) -> List[LogInfo]:
        logs = session.query(Log).all()
        return ([LogInfo(**log.__dict__) for log in logs])

    @session_manager
    def add_duplicate_info(self, session, duplicate_infos: list[DuplicateInfo]):
        # TODO: Add test for this method when testing CollectorDatabaseProcessor
        for duplicate_info in duplicate_infos:
            duplicate = Duplicate(
                batch_id=duplicate_info.batch_id,
                original_url_id=duplicate_info.original_url_id,
            )
            session.add(duplicate)

    @session_manager
    def get_batch_status(self, session, batch_id: int) -> BatchStatus:
        batch = session.query(Batch).filter_by(id=batch_id).first()
        return BatchStatus(batch.status)

    @session_manager
    def get_recent_batch_status_info(
        self,
        session,
        limit: int,
        collector_type: Optional[CollectorType] = None,
        status: Optional[BatchStatus] = None,
    ) -> List[BatchStatusInfo]:
        # Get only the batch_id, collector_type, status, and created_at
        query = session.query(Batch).order_by(Batch.date_generated.desc()).limit(limit)
        query = query.with_entities(Batch.id, Batch.strategy, Batch.status, Batch.date_generated)
        if collector_type:
            query = query.filter(Batch.strategy == collector_type.value)
        if status:
            query = query.filter(Batch.status == status.value)
        batches = query.all()
        return [BatchStatusInfo(**self.row_to_dict(batch)) for batch in batches]

if __name__ == "__main__":
    client = DatabaseClient()
    print("Database client initialized.")
