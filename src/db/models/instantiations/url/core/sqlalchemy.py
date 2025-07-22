from sqlalchemy import Column, Integer, ForeignKey, Text, String, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates import StandardModel
from src.db.models.types import record_type_values


class URL(UpdatedAtMixin, CreatedAtMixin, StandardModel):
    __tablename__ = 'urls'

    # The batch this URL is associated with
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
            'not relevant',
            'duplicate',
            'error',
            '404 not found',
            'individual record',
            name='url_status'
        ),
        nullable=False
    )
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=True)

    # Relationships
    batch = relationship(
        "Batch",
        secondary="link_batch_urls",
        back_populates="urls",
        uselist=False
    )
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
    data_source = relationship(
        "URLDataSource",
        back_populates="url",
        uselist=False
    )
    checked_for_duplicate = relationship(
        "URLCheckedForDuplicate",
        uselist=False,
        back_populates="url"
    )
    probed_for_404 = relationship(
        "URLProbedFor404",
        uselist=False,
        back_populates="url"
    )
    compressed_html = relationship(
        "URLCompressedHTML",
        uselist=False,
        back_populates="url"
    )