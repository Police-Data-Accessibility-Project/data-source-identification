"""
SQLAlchemy ORM models
"""
from sqlalchemy import func, Column, Integer, String, TIMESTAMP, Float, JSON, ForeignKey, Text, UniqueConstraint, \
    Boolean, DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship

from collector_db.enums import PGEnum
from core.enums import BatchStatus
from util.helper_functions import get_enum_values

# Base class for SQLAlchemy ORM models
Base = declarative_base()

status_check_string = ", ".join([f"'{status}'" for status in get_enum_values(BatchStatus)])

CURRENT_TIME_SERVER_DEFAULT = func.now()

batch_status_enum = PGEnum('complete', 'error', 'in-process', 'aborted', name='batch_status')

class Batch(Base):
    __tablename__ = 'batches'

    id = Column(Integer, primary_key=True)
    strategy = Column(
        postgresql.ENUM(
            'example',
            'ckan',
            'muckrock_county_search',
            'auto_googler',
            'muckrock_all_search',
            'muckrock_simple_search',
            'common_crawler',
            name='batch_strategy'),
        nullable=False)
    user_id = Column(Integer, nullable=False)
    # Gives the status of the batch
    status = Column(
        batch_status_enum,
        nullable=False
    )
    # The number of URLs in the batch
    # TODO: Add means to update after execution
    total_url_count = Column(Integer, nullable=False, default=0)
    original_url_count = Column(Integer, nullable=False, default=0)
    duplicate_url_count = Column(Integer, nullable=False, default=0)
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
        postgresql.ENUM(
            'pending',
            'submitted',
            'human_labeling',
            'rejected',
            'duplicate',
            'error',
            name='url_status'
        ),
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
    tasks = relationship(
        "Task",
        secondary="link_task_urls",
        back_populates="urls",
    )
    automated_agency_suggestions = relationship("AutomatedUrlAgencySuggestion", back_populates="url")
    user_agency_suggestions = relationship("UserUrlAgencySuggestion", back_populates="url")
    confirmed_agencies = relationship("ConfirmedUrlAgency", back_populates="url")


# URL Metadata table definition
class URLMetadata(Base):
    __tablename__ = 'url_metadata'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "attribute",
        name="uq_url_id_attribute"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey('urls.id', name='url_metadata_url_id_fkey'), nullable=False)
    attribute = Column(
        PGEnum('Record Type', 'Agency', 'Relevant', name='url_attribute'),
        nullable=False)
    value = Column(Text, nullable=False)
    validation_status = Column(
        PGEnum('Pending Validation', 'Validated', name='metadata_validation_status'),
        nullable=False)
    validation_source = Column(
        PGEnum('Machine Learning', 'Label Studio', 'Manual', name='validation_source'),
        nullable=False
    )
    notes = Column(Text, nullable=True)


    # Timestamps
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    url = relationship("URL", back_populates="url_metadata")
    annotations = relationship("MetadataAnnotation", back_populates="url_metadata")

class MetadataAnnotation(Base):
    __tablename__ = 'metadata_annotations'
    __table_args__ = (UniqueConstraint(
        "user_id",
        "metadata_id",
        name="metadata_annotations_uq_user_id_metadata_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    metadata_id = Column(Integer, ForeignKey('url_metadata.id'), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    url_metadata = relationship("URLMetadata", back_populates="annotations")

class RootURL(Base):
    __tablename__ = 'root_url_cache'
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


class URLErrorInfo(Base):
    __tablename__ = 'url_error_info'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "task_id",
        name="uq_url_id_error"),
    )

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    error = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)

    # Relationships
    url = relationship("URL", back_populates="error_info")
    task = relationship("Task", back_populates="errored_urls")

class URLHTMLContent(Base):
    __tablename__ = 'url_html_content'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "content_type",
        name="uq_url_id_content_type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
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

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    task_type = Column(
        PGEnum(
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            name='task_type'
        ), nullable=False)
    task_status = Column(batch_status_enum, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Relationships
    urls = relationship(
        "URL",
        secondary="link_task_urls",
        back_populates="tasks"
    )
    error = relationship("TaskError", back_populates="task")
    errored_urls = relationship("URLErrorInfo", back_populates="task")

class LinkTaskURL(Base):
    __tablename__ = 'link_task_urls'
    __table_args__ = (UniqueConstraint(
        "task_id",
        "url_id",
        name="uq_task_id_url_id"),
    )

    task_id = Column(Integer, ForeignKey('tasks.id', ondelete="CASCADE"), primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id', ondelete="CASCADE"), primary_key=True)



class TaskError(Base):
    __tablename__ = 'task_errors'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete="CASCADE"), nullable=False)
    error = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Relationships
    task = relationship("Task", back_populates="error")

    __table_args__ = (UniqueConstraint(
        "task_id",
        "error",
        name="uq_task_id_error"),
    )

class Agency(Base):
    __tablename__ = "agencies"

    agency_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=True)
    county = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=func.now())

    # Relationships
    confirmed_urls = relationship("ConfirmedUrlAgency", back_populates="agency")
    automated_suggestions = relationship("AutomatedUrlAgencySuggestion", back_populates="agency")
    user_suggestions = relationship("UserUrlAgencySuggestion", back_populates="agency")


class ConfirmedUrlAgency(Base):
    __tablename__ = "confirmed_url_agency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey("agencies.agency_id"), nullable=False)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)

    agency = relationship("Agency", back_populates="confirmed_urls")
    url = relationship("URL", back_populates="confirmed_agencies")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", name="uq_confirmed_url_agency"),
    )


class AutomatedUrlAgencySuggestion(Base):
    __tablename__ = "automated_url_agency_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey("agencies.agency_id"), nullable=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    is_unknown = Column(Boolean, nullable=True)

    agency = relationship("Agency", back_populates="automated_suggestions")
    url = relationship("URL", back_populates="automated_agency_suggestions")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", name="uq_automated_url_agency_suggestions"),
    )


class UserUrlAgencySuggestion(Base):
    __tablename__ = "user_url_agency_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agency_id = Column(Integer, ForeignKey("agencies.agency_id"), nullable=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    is_new = Column(Boolean, nullable=True)

    agency = relationship("Agency", back_populates="user_suggestions")
    url = relationship("URL", back_populates="user_agency_suggestions")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", "user_id", name="uq_user_url_agency_suggestions"),
    )