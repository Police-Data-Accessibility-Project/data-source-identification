from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.db.models.mixins import BatchDependentMixin
from src.db.models.templates import StandardBase


class Duplicate(BatchDependentMixin, StandardBase):
    """
    Identifies duplicates which occur within a batch
    """
    __tablename__ = 'duplicates'

    original_url_id = Column(
        Integer,
        ForeignKey('urls.id'),
        nullable=False,
        doc="The original URL ID"
    )

    # Relationships
    batch = relationship("Batch", back_populates="duplicates")
    original_url = relationship("URL", back_populates="duplicates")
