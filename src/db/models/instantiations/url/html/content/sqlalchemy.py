from sqlalchemy import UniqueConstraint, Column, Text
from sqlalchemy.orm import relationship

from src.db.enums import PGEnum
from src.db.models.mixins import UpdatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class URLHTMLContent(
    UpdatedAtMixin,
    URLDependentMixin,
    WithIDBase
):
    __tablename__ = 'url_html_content'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "content_type",
        name="uq_url_id_content_type"),
    )

    content_type = Column(
        PGEnum('Title', 'Description', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Div', name='url_html_content_type'),
        nullable=False)
    content = Column(Text, nullable=False)


    # Relationships
    url = relationship("URL", back_populates="html_content")
