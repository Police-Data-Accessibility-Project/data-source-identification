from sqlalchemy import Column, Text
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, BatchDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class Log(CreatedAtMixin, BatchDependentMixin, WithIDBase):
    __tablename__ = 'logs'

    log = Column(Text, nullable=False)

    # Relationships
    batch = relationship("Batch", back_populates="logs")
