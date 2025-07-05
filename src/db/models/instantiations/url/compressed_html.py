from sqlalchemy import Column, LargeBinary
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates import StandardModel


class URLCompressedHTML(
    CreatedAtMixin,
    URLDependentMixin,
    StandardModel
):
    __tablename__ = 'url_compressed_html'

    compressed_html = Column(LargeBinary, nullable=False)

    url = relationship(
        "URL",
        uselist=False,
        back_populates="compressed_html"
    )