from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates import StandardModel


class URLDataSource(CreatedAtMixin, URLDependentMixin, StandardModel):
    __tablename__ = "url_data_sources"

    data_source_id = Column(Integer, nullable=False)

    # Relationships
    url = relationship(
        "URL",
        back_populates="data_source",
        uselist=False
    )
