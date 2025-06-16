from sqlalchemy import UniqueConstraint, Column, String

from src.db.models.mixins import UpdatedAtMixin
from src.db.models.templates import StandardModel


class RootURL(UpdatedAtMixin, StandardModel):
    __tablename__ = 'root_url_cache'
    __table_args__ = (
        UniqueConstraint(
        "url",
        name="uq_root_url_url"),
    )

    url = Column(String, nullable=False)
    page_title = Column(String, nullable=False)
    page_description = Column(String, nullable=True)
