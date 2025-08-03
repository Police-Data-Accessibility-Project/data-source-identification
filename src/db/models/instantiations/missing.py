from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.models.helpers import get_created_at_column
from src.db.models.mixins import BatchDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class Missing(BatchDependentMixin, WithIDBase):
    __tablename__ = 'missing'

    place_id = Column(Integer, nullable=False)
    record_type = Column(String, nullable=False)
    strategy_used = Column(Text, nullable=False)
    date_searched = get_created_at_column()

    # Relationships
    batch = relationship("Batch")
