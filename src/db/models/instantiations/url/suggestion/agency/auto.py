from sqlalchemy import Column, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class AutomatedUrlAgencySuggestion(URLDependentMixin, WithIDBase):
    __tablename__ = "automated_url_agency_suggestions"

    agency_id = get_agency_id_foreign_column(nullable=True)
    is_unknown = Column(Boolean, nullable=True)

    agency = relationship("Agency", back_populates="automated_suggestions")
    url = relationship("URL", back_populates="automated_agency_suggestions")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", name="uq_automated_url_agency_suggestions"),
    )
