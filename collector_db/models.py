"""
SQLAlchemy ORM models
"""
from sqlalchemy import func, Column, Integer, String, CheckConstraint, TIMESTAMP, Float, JSON, ForeignKey, Text, Enum, \
    UniqueConstraint, TypeDecorator
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship

from core.enums import BatchStatus
from util.helper_functions import get_enum_values
from enum import Enum as PyEnum
# Base class for SQLAlchemy ORM models
Base = declarative_base()

status_check_string = ", ".join([f"'{status}'" for status in get_enum_values(BatchStatus)])

CURRENT_TIME_SERVER_DEFAULT = func.now()

class PGEnum(TypeDecorator):
    impl = postgresql.ENUM

    def process_bind_param(self, value: PyEnum, dialect):
        # Convert Python Enum to its value before binding to the DB
        if isinstance(value, PyEnum):
            return value.value
        return value

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

    # Relationships
    urls = relationship("URL", back_populates="batch")
    missings = relationship("Missing", back_populates="batch")
    logs = relationship("Log", back_populates="batch")
    duplicates = relationship("Duplicate", back_populates="batch")


class URL(Base):
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True)
    # The batch this URL is associated with
    batch_id = Column(Integer, ForeignKey('batches.id', name='fk_url_batch_id'), nullable=False)
    url = Column(Text, unique=True)
    # The metadata from the collector
    collector_metadata = Column(JSON)
    # The outcome of the URL: submitted, human_labeling, rejected, duplicate, etc.
    outcome = Column(
        postgresql.ENUM('pending', 'submitted', 'human_labeling', 'rejected', 'duplicate', 'error', name='url_status'),
        nullable=False
    )
    created_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Relationships
    batch = relationship("Batch", back_populates="urls")
    duplicates = relationship("Duplicate", back_populates="original_url")
    url_metadata = relationship("URLMetadata", back_populates="url", cascade="all, delete-orphan")
    html_content = relationship("URLHTMLContent", back_populates="url", cascade="all, delete-orphan")
    error_info = relationship("URLErrorInfo", back_populates="url", cascade="all, delete-orphan")


class URLAttributeType(PyEnum):
    RECORD_TYPE = "Record Type"
    AGENCY = "Agency"
    RELEVANT = "Relevant"

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
        PGEnum('Record Type', 'Agency', 'Relevant', name='url_attribute'),
        nullable=False)
    value = Column(Text, nullable=False)
    validation_status = Column(
        PGEnum('Pending Label Studio', 'Validated', name='validation_status'),
        nullable=False)
    validation_source = Column(
        PGEnum('Machine Learning', 'Label Studio', 'Manual', name='validation_source'),
        nullable=False
    )

    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    url = relationship("URL", back_populates="url_metadata")

class RootURL(Base):
    __tablename__ = 'root_urls'
    __table_args__ = (
        UniqueConstraint(
        "url",
        name="uq_root_url_url"),
    )

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    page_title = Column(String, nullable=False)
    page_description = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

class URLHTMLContentType(PyEnum):
    TITLE = "Title"
    DESCRIPTION = "Description"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H5 = "H5"
    H6 = "H6"
    DIV = "Div"

class URLErrorInfo(Base):
    __tablename__ = 'url_error_info'

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    error = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Relationships
    url = relationship("URL", back_populates="error_info")

class URLHTMLContent(Base):
    __tablename__ = 'url_html_content'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "content_type",
        name="uq_url_id_content_type"),
    )

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    content_type = Column(
        PGEnum('Title', 'Description', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Div', name='url_html_content_type'),
        nullable=False)
    content = Column(Text, nullable=False)

    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    url = relationship("URL", back_populates="html_content")

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

    # Relationships
    batch = relationship("Batch", back_populates="duplicates")
    original_url = relationship("URL", back_populates="duplicates")



class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('batches.id'), nullable=False)
    log = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Relationships
    batch = relationship("Batch", back_populates="logs")

class Missing(Base):
    __tablename__ = 'missing'

    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, nullable=False)
    record_type = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    strategy_used = Column(Text, nullable=False)
    date_searched = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Relationships
    batch = relationship("Batch", back_populates="missings")
