from sqlalchemy import Column, Integer, TIMESTAMP, Float, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.helpers import CURRENT_TIME_SERVER_DEFAULT
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import batch_status_enum


class Batch(WithIDBase):
    __tablename__ = 'batches'

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
    urls = relationship(
        "URL",
        secondary="link_batch_urls",
        back_populates="batch",
        overlaps="url"
    )
    # missings = relationship("Missing", back_populates="batch")  # Not in active use
    logs = relationship("Log", back_populates="batch")
    duplicates = relationship("Duplicate", back_populates="batch")
