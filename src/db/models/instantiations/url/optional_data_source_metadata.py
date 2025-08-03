from sqlalchemy import Column, ARRAY, String
from sqlalchemy.orm import relationship

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class URLOptionalDataSourceMetadata(URLDependentMixin, WithIDBase):
    __tablename__ = 'url_optional_data_source_metadata'

    record_formats = Column(ARRAY(String), nullable=True)
    data_portal_type = Column(String, nullable=True)
    supplying_entity = Column(String, nullable=True)

    # Relationships
    url = relationship("URL", uselist=False, back_populates="optional_data_source_metadata")
