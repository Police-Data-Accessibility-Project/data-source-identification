from sqlalchemy import Column, Boolean, UniqueConstraint, Integer
from sqlalchemy.orm import relationship

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class UserUrlAgencySuggestion(URLDependentMixin, WithIDBase):
    __tablename__ = "user_url_agency_suggestions"

    agency_id = get_agency_id_foreign_column(nullable=True)
    user_id = Column(Integer, nullable=False)
    is_new = Column(Boolean, nullable=True)

    agency = relationship("Agency", back_populates="user_suggestions")
    url = relationship("URL", back_populates="user_agency_suggestion")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", "user_id", name="uq_user_url_agency_suggestions"),
    )
