from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class URLDataSource(CreatedAtMixin, URLDependentMixin, WithIDBase):
    __tablename__ = "url_data_source"

    data_source_id = Column(Integer, nullable=False)

    # Relationships
    url = relationship(
        "URL",
        back_populates="data_source",
        uselist=False
    )
