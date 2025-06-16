from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin
from src.db.models.templates import Base


class Agency(UpdatedAtMixin, Base):
    __tablename__ = "agencies"

    agency_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=True)
    county = Column(String, nullable=True)
    locality = Column(String, nullable=True)

    # Relationships
    automated_suggestions = relationship("AutomatedUrlAgencySuggestion", back_populates="agency")
    user_suggestions = relationship("UserUrlAgencySuggestion", back_populates="agency")
    confirmed_urls = relationship("ConfirmedURLAgency", back_populates="agency")
