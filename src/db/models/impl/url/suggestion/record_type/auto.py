from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.mixins import URLDependentMixin, UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import record_type_values


class AutoRecordTypeSuggestion(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    WithIDBase
):
    __tablename__ = "auto_record_type_suggestions"
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=False)

    __table_args__ = (
        UniqueConstraint("url_id", name="auto_record_type_suggestions_uq_url_id"),
    )

    # Relationships

    url = relationship("URL", back_populates="auto_record_type_suggestion")


