from sqlalchemy import UniqueConstraint, Column, Integer
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class ReviewingUserURL(CreatedAtMixin, URLDependentMixin, WithIDBase):
    __tablename__ = 'reviewing_user_url'
    __table_args__ = (
        UniqueConstraint(
        "url_id",
        name="approving_user_url_uq_user_id_url_id"),
    )
    user_id = Column(Integer, nullable=False)

    # Relationships
    url = relationship("URL", uselist=False, back_populates="reviewing_user")
