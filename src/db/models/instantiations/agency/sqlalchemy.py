"""
References an agency in the data sources database.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates import Base, StandardBase


class Agency(
    CreatedAtMixin, # When agency was added to database
    UpdatedAtMixin, # When agency was last updated in database
    StandardBase
):
    __tablename__ = "agencies"

    # TODO: Rename agency_id to ds_agency_id

    agency_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=True)
    county = Column(String, nullable=True)
    locality = Column(String, nullable=True)
    ds_last_updated_at = Column(
        DateTime,
        nullable=True,
        comment="The last time the agency was updated in the data sources database."
    )

    # Relationships
    automated_suggestions = relationship("AutomatedUrlAgencySuggestion", back_populates="agency")
    user_suggestions = relationship("UserUrlAgencySuggestion", back_populates="agency")
    confirmed_urls = relationship("LinkURLAgency", back_populates="agency")
