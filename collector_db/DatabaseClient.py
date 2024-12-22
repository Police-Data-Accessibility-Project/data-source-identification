from functools import wraps

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, ForeignKey, CheckConstraint, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from typing import Optional, Dict, Any, List

from collector_db.BatchInfo import BatchInfo
from collector_db.URLInfo import URLInfo

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# SQLAlchemy ORM models
class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True)
    strategy = Column(String, nullable=False)
    status = Column(String, CheckConstraint("status IN ('in-process', 'complete', 'error')"), nullable=False)
    count = Column(Integer, nullable=False)
    date_generated = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    strategy_success_rate = Column(Float)
    metadata_success_rate = Column(Float)
    agency_match_rate = Column(Float)
    record_type_match_rate = Column(Float)
    record_category_match_rate = Column(Float)
    compute_time = Column(Integer)
    parameters = Column(JSON)

    urls = relationship("URL", back_populates="batch")
    missings = relationship("Missing", back_populates="batch")


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    url = Column(Text, unique=True)
    url_metadata = Column(JSON)
    outcome = Column(String)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")

    batch = relationship("Batch", back_populates="urls")


class Missing(Base):
    __tablename__ = 'missing'

    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, nullable=False)
    record_type = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    strategy_used = Column(Text, nullable=False)
    date_searched = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")

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

    @session_manager
    def insert_batch(self, batch_info: BatchInfo) -> Batch:
        """Insert a new batch into the database."""
        batch = Batch(
            **batch_info.model_dump()
        )
        self.session.add(batch)
        return batch

    @session_manager
    def get_batch_by_id(self, batch_id: int) -> Optional[BatchInfo]:
        """Retrieve a batch by ID."""
        batch = self.session.query(Batch).filter_by(id=batch_id).first()
        return BatchInfo(**batch.__dict__)

    @session_manager
    def insert_url(self, url_info: URLInfo):
        """Insert a new URL into the database."""
        url_entry = URL(
            **url_info.model_dump()
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
