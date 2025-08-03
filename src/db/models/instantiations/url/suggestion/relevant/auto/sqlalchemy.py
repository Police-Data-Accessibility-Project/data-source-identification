from sqlalchemy import Column, Boolean, UniqueConstraint, String, Float
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class AutoRelevantSuggestion(UpdatedAtMixin, CreatedAtMixin, URLDependentMixin, WithIDBase):
    __tablename__ = "auto_relevant_suggestions"

    relevant = Column(Boolean, nullable=True)
    confidence = Column(Float, nullable=True)
    model_name = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("url_id", name="auto_relevant_suggestions_uq_url_id"),
    )

    # Relationships

    url = relationship("URL", back_populates="auto_relevant_suggestion")
