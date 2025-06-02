from functools import wraps
from typing import Optional, List

from sqlalchemy import create_engine, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from src.collectors.enums import URLStatus
from src.db.config_manager import ConfigManager
from src.db.dtos.batch_info import BatchInfo
from src.db.dtos.duplicate_info import DuplicateInsertInfo
from src.db.dtos.insert_urls_info import InsertURLsInfo
from src.db.dtos.log_info import LogInfo
from src.db.dtos.url_info import URLInfo
from src.db.dtos.url_mapping import URLMapping
from src.db.models.templates import Base
from src.db.models.core import Batch, URL, Log, Duplicate, URLDataSource
from src.core.tasks.operators.submit_approved_url.tdo import SubmittedURLInfo
from src.core.env_var_manager import EnvVarManager
from src.core.enums import BatchStatus


# Database Client
class DatabaseClient:
    def __init__(self, db_url: Optional[str] = None):
        """Initialize the DatabaseClient."""
        if db_url is None:
            db_url = EnvVarManager.get().get_postgres_connection_string(is_async=True)

        self.engine = create_engine(
            url=db_url,
            echo=ConfigManager.get_sqlalchemy_echo(),
        )
        self.session_maker = scoped_session(sessionmaker(bind=self.engine))
        self.session = None

    def init_db(self):
        Base.metadata.create_all(self.engine)

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

    @session_manager
    def insert_batch(self, session, batch_info: BatchInfo) -> int:
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
        session.commit()
        session.refresh(batch)
        return batch.id

    @session_manager
    def get_batch_by_id(self, session, batch_id: int) -> Optional[BatchInfo]:
        """Retrieve a batch by ID."""
        batch = session.query(Batch).filter_by(id=batch_id).first()
        return BatchInfo(**batch.__dict__)


    @session_manager
    def insert_duplicates(self, session, duplicate_infos: list[DuplicateInsertInfo]):
        for duplicate_info in duplicate_infos:
            duplicate = Duplicate(
                batch_id=duplicate_info.duplicate_batch_id,
                original_url_id=duplicate_info.original_url_id,
            )
            session.add(duplicate)


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
            collector_metadata=url_info.collector_metadata,
            outcome=url_info.outcome.value,
            name=url_info.name
        )
        if url_info.created_at is not None:
            url_entry.created_at = url_info.created_at
        session.add(url_entry)
        session.commit()
        session.refresh(url_entry)
        return url_entry.id

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
                duplicate_info = DuplicateInsertInfo(
                    duplicate_batch_id=batch_id,
                    original_url_id=orig_url_info.id
                )
                duplicates.append(duplicate_info)
        self.insert_duplicates(duplicates)

        return InsertURLsInfo(
            url_mappings=url_mappings,
            total_count=len(url_infos),
            original_count=len(url_mappings),
            duplicate_count=len(duplicates),
            url_ids=[url_mapping.url_id for url_mapping in url_mappings]
        )

    @session_manager
    def get_urls_by_batch(self, session, batch_id: int, page: int = 1) -> List[URLInfo]:
        """Retrieve all URLs associated with a batch."""
        urls = (session.query(URL).filter_by(batch_id=batch_id)
                .order_by(URL.id).limit(100).offset((page - 1) * 100).all())
        return ([URLInfo(**url.__dict__) for url in urls])

    @session_manager
    def insert_logs(self, session, log_infos: List[LogInfo]):
        for log_info in log_infos:
            log = Log(log=log_info.log, batch_id=log_info.batch_id)
            if log_info.created_at is not None:
                log.created_at = log_info.created_at
            session.add(log)

    @session_manager
    def get_batch_status(self, session, batch_id: int) -> BatchStatus:
        batch = session.query(Batch).filter_by(id=batch_id).first()
        return BatchStatus(batch.status)

    @session_manager
    def update_url(self, session, url_info: URLInfo):
        url = session.query(URL).filter_by(id=url_info.id).first()
        url.collector_metadata = url_info.collector_metadata

    @session_manager
    def mark_urls_as_submitted(
            self,
            session: Session,
            infos: list[SubmittedURLInfo]
    ):
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

            session.execute(query)

if __name__ == "__main__":
    client = DatabaseClient()
    print("Database client initialized.")
