"""
SQLAlchemy ORM models
"""
from sqlalchemy import func, Column, Integer, String, CheckConstraint, TIMESTAMP, Float, JSON, ForeignKey, Text, Enum, \
    UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship

from core.enums import BatchStatus
from util.helper_functions import get_enum_values
from enum import Enum as PyEnum
# Base class for SQLAlchemy ORM models
Base = declarative_base()

status_check_string = ", ".join([f"'{status}'" for status in get_enum_values(BatchStatus)])

CURRENT_TIME_SERVER_DEFAULT = func.now()


class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True)
    strategy = Column(
        postgresql.ENUM(
            'example', 'ckan', 'muckrock_county_search', 'auto_googler', 'muckrock_all_search', 'muckrock_simple_search', 'common_crawler',
            name='batch_strategy'),
        nullable=False)
    user_id = Column(Integer, nullable=False)
    # Gives the status of the batch
    status = Column(
        postgresql.ENUM(
            'complete', 'error', 'in-process', 'aborted',
            name='batch_status'),
        nullable=False
    )
    # The number of URLs in the batch
    # TODO: Add means to update after execution
    total_url_count = Column(Integer, nullable=False)
    original_url_count = Column(Integer, nullable=False)
    duplicate_url_count = Column(Integer, nullable=False)
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
    logs = relationship("Log", back_populates="batch")
    duplicates = relationship("Duplicate", back_populates="batch")


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    # The batch this URL is associated with
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    url = Column(Text, unique=True)
    # The metadata from the collector
    collector_metadata = Column(JSON)
    # The outcome of the URL: submitted, human_labeling, rejected, duplicate, etc.
    outcome = Column(
        postgresql.ENUM('pending', 'submitted', 'human_labeling', 'rejected', 'duplicate', name='url_outcome'),
        nullable=False
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    batch = relationship("Batch", back_populates="urls")
    duplicates = relationship("Duplicate", back_populates="original_url")
    url_metadata = relationship("URLMetadata", back_populates="url", cascade="all, delete-orphan")


class URLAttributeType(PyEnum):
    RECORD_TYPE = "record_type"
    AGENCY = "agency"
    RELEVANT = "relevant"

class ValidationStatus(PyEnum):
    PENDING_LABEL_STUDIO = "Pending Label Studio"
    VALIDATED = "Validated"

class ValidationSource(PyEnum):
    MACHINE_LEARNING = "Machine Learning"
    LABEL_STUDIO = "Label Studio"
    MANUAL = "Manual"

# URL Metadata table definition
class URLMetadata(Base):
    __tablename__ = 'url_metadata'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "attribute",
        name="model_num2_key"),
    )

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    attribute = Column(
        postgresql.ENUM('Record Type', 'Agency', 'Relevant', name='url_attribute'),
        nullable=False)
    value = Column(Text, nullable=False)
    validation_status = Column(
        postgresql.ENUM('Pending Label Studio', 'Validated', name='validation_status'),
        nullable=False)
    validation_source = Column(
        postgresql.ENUM('Machine Learning', 'Label Studio', 'Manual', name='validation_source'),
        nullable=False
    )

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    url = relationship("URL", back_populates="url_metadata")


class Duplicate(Base):
    """
    Identifies duplicates which occur within a batch
    """
    __tablename__ = 'duplicates'

    id = Column(Integer, primary_key=True)
    batch_id = Column(
        Integer,
        ForeignKey('batches.id'),
        nullable=False,
        doc="The batch that produced the duplicate"
    )
    original_url_id = Column(
        Integer,
        ForeignKey('urls.id'),
        nullable=False,
        doc="The original URL ID"
    )

    batch = relationship("Batch", back_populates="duplicates")
    original_url = relationship("URL", back_populates="duplicates")



class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    log = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    batch = relationship("Batch", back_populates="logs")

class Missing(Base):
    __tablename__ = 'missing'

    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, nullable=False)
    record_type = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    strategy_used = Column(Text, nullable=False)
    date_searched = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    batch = relationship("Batch", back_populates="missings")
