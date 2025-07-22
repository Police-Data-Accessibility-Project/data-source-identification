from sqlalchemy import Column, UniqueConstraint, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates import StandardModel


class UserRelevantSuggestion(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    StandardModel
):
    __tablename__ = "user_relevant_suggestions"

    user_id = Column(Integer, nullable=False)
    suggested_status = Column(
        postgresql.ENUM(
            'relevant',
            'not relevant',
            'individual record',
            'broken page/404 not found',
            name='suggested_status'
        ),
        nullable=True
    )

    __table_args__ = (
        UniqueConstraint("url_id", "user_id", name="uq_user_relevant_suggestions"),
    )

    # Relationships

    url = relationship("URL", back_populates="user_relevant_suggestion")
