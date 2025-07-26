from sqlalchemy import Column, Integer, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates import StandardBase
from src.db.models.types import record_type_values


class UserRecordTypeSuggestion(UpdatedAtMixin, CreatedAtMixin, URLDependentMixin, StandardBase):
    __tablename__ = "user_record_type_suggestions"

    user_id = Column(Integer, nullable=False)
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=False)

    __table_args__ = (
        UniqueConstraint("url_id", "user_id", name="uq_user_record_type_suggestions"),
    )

    # Relationships

    url = relationship("URL", back_populates="user_record_type_suggestion")
