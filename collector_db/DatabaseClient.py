from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from typing import Optional, List

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInfo
from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.models import Base, Batch, URL
from core.enums import BatchStatus



# SQLAlchemy ORM models


# Database Client
class DatabaseClient:
    def __init__(self, db_url: str = "sqlite:///database.db"):
        """Initialize the DatabaseClient."""
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session = None

    def session_manager(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            self.session = self.session_maker()
            try:
                result = method(self, *args, **kwargs)
                self.session.commit()
                return result
            except Exception as e:
                self.session.rollback()
                raise e
            finally:
                self.session.close()
                self.session = None

        return wrapper

    @session_manager
    def insert_batch(self, batch_info: BatchInfo) -> int:
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
        self.session.add(batch)
        self.session.commit()
        self.session.refresh(batch)
        return batch.id

    @session_manager
    def update_batch_post_collection(
        self,
        batch_id: int,
        url_count: int,
        batch_status: BatchStatus,
        compute_time: float = None,
    ):
        batch = self.session.query(Batch).filter_by(id=batch_id).first()
        batch.count = url_count
        batch.status = batch_status.value
        batch.compute_time = compute_time

    @session_manager
    def get_batch_by_id(self, batch_id: int) -> Optional[BatchInfo]:
        """Retrieve a batch by ID."""
        batch = self.session.query(Batch).filter_by(id=batch_id).first()
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
    def get_url_info_by_url(self, url: str) -> Optional[URLInfo]:
        url = self.session.query(URL).filter_by(url=url).first()
        return URLInfo(**url.__dict__)

    @session_manager
    def insert_url(self, url_info: URLInfo) -> int:
        """Insert a new URL into the database."""
        url_entry = URL(
            batch_id=url_info.batch_id,
            url=url_info.url,
            url_metadata=url_info.url_metadata,
            outcome=url_info.outcome.value
        )
        self.session.add(url_entry)
        self.session.commit()
        self.session.refresh(url_entry)
        return url_entry.id


    @session_manager
    def get_urls_by_batch(self, batch_id: int) -> List[URLInfo]:
        """Retrieve all URLs associated with a batch."""
        urls = self.session.query(URL).filter_by(batch_id=batch_id).all()
        return ([URLInfo(**url.__dict__) for url in urls])

    @session_manager
    def is_duplicate_url(self, url: str) -> bool:
        result = self.session.query(URL).filter_by(url=url).first()
        return result is not None

if __name__ == "__main__":
    client = DatabaseClient()
    print("Database client initialized.")
