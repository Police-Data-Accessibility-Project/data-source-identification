from sqlalchemy import UniqueConstraint, Column
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates import StandardBase


class LinkURLAgency(URLDependentMixin, StandardBase):
    __tablename__ = "link_urls_agencies"

    agency_id: Mapped[int] = get_agency_id_foreign_column()

    url = relationship("URL", back_populates="confirmed_agencies")
    agency = relationship("Agency", back_populates="confirmed_urls")

    __table_args__ = (
        UniqueConstraint("url_id", "agency_id", name="uq_confirmed_url_agency"),
    )
