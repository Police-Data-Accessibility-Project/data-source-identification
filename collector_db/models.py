"""
SQLAlchemy ORM models
"""
from sqlalchemy import func, Column, Integer, String, TIMESTAMP, Float, JSON, ForeignKey, Text, UniqueConstraint, \
    Boolean, DateTime, ARRAY
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship

from collector_db.enums import PGEnum, TaskType
from core.enums import BatchStatus, RecordType
from util.helper_functions import get_enum_values

# Base class for SQLAlchemy ORM models
Base = declarative_base()

status_check_string = ", ".join([f"'{status}'" for status in get_enum_values(BatchStatus)])

CURRENT_TIME_SERVER_DEFAULT = func.now()

batch_status_enum = PGEnum('ready to label', 'error', 'in-process', 'aborted', name='batch_status')

record_type_values = get_enum_values(RecordType)

def get_created_at_column():
    return Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

def get_updated_at_column():
    return Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT, onupdate=CURRENT_TIME_SERVER_DEFAULT)


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
            'manual',
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
    name = Column(String)
    description = Column(Text)
    # The metadata from the collector
    collector_metadata = Column(JSON)
    # The outcome of the URL: submitted, human_labeling, rejected, duplicate, etc.
    outcome = Column(
        postgresql.ENUM(
            'pending',
            'submitted',
            'validated',
            'rejected',
            'duplicate',
            'error',
            name='url_status'
        ),
        nullable=False
    )
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=True)
    created_at = get_created_at_column()
    updated_at = get_updated_at_column()
    data_source_id = Column(Integer, nullable=True)

    # Relationships
    batch = relationship("Batch", back_populates="urls")
    duplicates = relationship("Duplicate", back_populates="original_url")
    html_content = relationship("URLHTMLContent", back_populates="url", cascade="all, delete-orphan")
    error_info = relationship("URLErrorInfo", back_populates="url", cascade="all, delete-orphan")
    tasks = relationship(
        "Task",
        secondary="link_task_urls",
        back_populates="urls",
    )
    automated_agency_suggestions = relationship(
        "AutomatedUrlAgencySuggestion", back_populates="url")
    user_agency_suggestion = relationship(
        "UserUrlAgencySuggestion", uselist=False, back_populates="url")
    auto_record_type_suggestion = relationship(
        "AutoRecordTypeSuggestion", uselist=False, back_populates="url")
    user_record_type_suggestion = relationship(
        "UserRecordTypeSuggestion", uselist=False, back_populates="url")
    auto_relevant_suggestion = relationship(
        "AutoRelevantSuggestion", uselist=False, back_populates="url")
    user_relevant_suggestion = relationship(
        "UserRelevantSuggestion", uselist=False, back_populates="url")
    reviewing_user = relationship(
        "ReviewingUserURL", uselist=False, back_populates="url")
    optional_data_source_metadata = relationship(
        "URLOptionalDataSourceMetadata", uselist=False, back_populates="url")
    confirmed_agencies = relationship(
        "ConfirmedURLAgency",
    )


class URLOptionalDataSourceMetadata(Base):
    __tablename__ = 'url_optional_data_source_metadata'

    id = Column(Integer, primary_key=True)
    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    record_formats = Column(ARRAY(String), nullable=True)
    data_portal_type = Column(String, nullable=True)
    supplying_entity = Column(String, nullable=True)

    # Relationships
    url = relationship("URL", uselist=False, back_populates="optional_data_source_metadata")

class ReviewingUserURL(Base):
    __tablename__ = 'reviewing_user_url'
    __table_args__ = (
        UniqueConstraint(
        "url_id",
        name="approving_user_url_uq_user_id_url_id"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    url_id = Column(Integer, ForeignKey('urls.id'), nullable=False)
    created_at = get_created_at_column()

    # Relationships
    url = relationship("URL", uselist=False, back_populates="reviewing_user")

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
    updated_at = get_updated_at_column()


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
    updated_at = get_updated_at_column()
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

    updated_at = get_updated_at_column()

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
    created_at = get_created_at_column()

    # Relationships
    batch = relationship("Batch", back_populates="logs")

class Missing(Base):
    __tablename__ = 'missing'

    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, nullable=False)
    record_type = Column(String, nullable=False)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    strategy_used = Column(Text, nullable=False)
    date_searched = get_created_at_column()

    # Relationships
    batch = relationship("Batch", back_populates="missings")

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    task_type = Column(
        PGEnum(
            *[task_type.value for task_type in TaskType],
            name='task_type'
        ), nullable=False)
    task_status = Column(batch_status_enum, nullable=False)
    updated_at = get_updated_at_column()

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
    updated_at = get_updated_at_column()

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
    updated_at = get_updated_at_column()

    # Relationships
    automated_suggestions = relationship("AutomatedUrlAgencySuggestion", back_populates="agency")
    user_suggestions = relationship("UserUrlAgencySuggestion", back_populates="agency")
    confirmed_urls = relationship("ConfirmedURLAgency", back_populates="agency")

class ConfirmedURLAgency(Base):
    __tablename__ = "confirmed_url_agency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    agency_id = Column(Integer, ForeignKey("agencies.agency_id"), nullable=False)

    url = relationship("URL", back_populates="confirmed_agencies")
    agency = relationship("Agency", back_populates="confirmed_urls")

    __table_args__ = (
        UniqueConstraint("url_id", "agency_id", name="uq_confirmed_url_agency"),
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
    url = relationship("URL", back_populates="user_agency_suggestion")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", "user_id", name="uq_user_url_agency_suggestions"),
    )

class AutoRelevantSuggestion(Base):
    __tablename__ = "auto_relevant_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    relevant = Column(Boolean, nullable=True)
    created_at = get_created_at_column()
    updated_at = get_updated_at_column()

    __table_args__ = (
        UniqueConstraint("url_id", name="auto_relevant_suggestions_uq_url_id"),
    )

    # Relationships

    url = relationship("URL", back_populates="auto_relevant_suggestion")


class AutoRecordTypeSuggestion(Base):
    __tablename__ = "auto_record_type_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=False)
    created_at = get_created_at_column()
    updated_at = get_updated_at_column()

    __table_args__ = (
        UniqueConstraint("url_id", name="auto_record_type_suggestions_uq_url_id"),
    )

    # Relationships

    url = relationship("URL", back_populates="auto_record_type_suggestion")

class UserRelevantSuggestion(Base):
    __tablename__ = "user_relevant_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    relevant = Column(Boolean, nullable=False)
    created_at = get_created_at_column()
    updated_at = get_updated_at_column()

    __table_args__ = (
        UniqueConstraint("url_id", "user_id", name="uq_user_relevant_suggestions"),
    )

    # Relationships

    url = relationship("URL", back_populates="user_relevant_suggestion")


class UserRecordTypeSuggestion(Base):
    __tablename__ = "user_record_type_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=False)
    created_at = get_created_at_column()
    updated_at = get_updated_at_column()

    __table_args__ = (
        UniqueConstraint("url_id", "user_id", name="uq_user_record_type_suggestions"),
    )

    # Relationships

    url = relationship("URL", back_populates="user_record_type_suggestion")

class BacklogSnapshot(Base):
    __tablename__ = "backlog_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    count_pending_total = Column(Integer, nullable=False)
    created_at = get_created_at_column()
