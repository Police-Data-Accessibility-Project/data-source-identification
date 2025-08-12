from sqlalchemy import Column, LargeBinary
from sqlalchemy.orm import relationship, Mapped

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class URLCompressedHTML(
    CreatedAtMixin,
    URLDependentMixin,
    WithIDBase
):
    __tablename__ = 'url_compressed_html'

    compressed_html: Mapped[bytes] = Column(LargeBinary, nullable=False)

    url = relationship(
        "URL",
        uselist=False,
        back_populates="compressed_html"
    )