from datetime import datetime
from functools import wraps

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, ForeignKey, CheckConstraint, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import Optional, Dict, Any, List

from sqlalchemy.sql.functions import current_timestamp, func
from torch.backends.opt_einsum import strategy

from collector_db.BatchInfo import BatchInfo
from collector_db.URLInfo import URLInfo
from core.enums import BatchStatus
from util.helper_functions import get_enum_values

# Base class for SQLAlchemy ORM models
Base = declarative_base()

status_check_string = ", ".join([f"'{status}'" for status in get_enum_values(BatchStatus)])

CURRENT_TIME_SERVER_DEFAULT = func.now()

# SQLAlchemy ORM models
class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True)
    strategy = Column(String, nullable=False)
    # Gives the status of the batch
    status = Column(String, CheckConstraint(f"status IN ({status_check_string})"), nullable=False)
    # The number of URLs in the batch
    # TODO: Add means to update after execution
    count = Column(Integer, nullable=False)
    date_generated = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)
    # How often URLs ended up approved in the database
    strategy_success_rate = Column(Float)
    # Percentage of metadata identified by models
    metadata_success_rate = Column(Float)
    # Rate of matching to agencies
    agency_match_rate = Column(Float)
    # Rate of matching to record types
    record_type_match_rate = Column(Float)
    # Rate of matching to record categories
    record_category_match_rate = Column(Float)
    # Time taken to generate the batch
    # TODO: Add means to update after execution
    compute_time = Column(Float)
    # The parameters used to generate the batch
    parameters = Column(JSON)

    urls = relationship("URL", back_populates="batch")
    missings = relationship("Missing", back_populates="batch")


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    # The batch this URL is associated with
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    url = Column(Text, unique=True)
    # The metadata associated with the URL
    url_metadata = Column(JSON)
    # The outcome of the URL: submitted, human_labeling, rejected, duplicate, etc.
    outcome = Column(String)
    created_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    batch = relationship("Batch", back_populates="urls")


class Missing(Base):
    __tablename__ = 'missing'

    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, nullable=False)
    record_type = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    strategy_used = Column(Text, nullable=False)
    date_searched = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    batch = relationship("Batch", back_populates="missings")


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

    def insert_urls(self, url_infos: List[URLInfo], batch_id: int):
        for url_info in url_infos:
            url_info.batch_id = batch_id
            self.insert_url(url_info)

    @session_manager
    def insert_url(self, url_info: URLInfo):
        """Insert a new URL into the database."""
        url_entry = URL(
            batch_id=url_info.batch_id,
            url=url_info.url,
            url_metadata=url_info.url_metadata,
            outcome=url_info.outcome.value
        )
        self.session.add(url_entry)

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
