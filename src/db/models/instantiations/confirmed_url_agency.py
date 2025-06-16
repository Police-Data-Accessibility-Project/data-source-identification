from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates import StandardModel


class ConfirmedURLAgency(URLDependentMixin, StandardModel):
    __tablename__ = "confirmed_url_agency"

    agency_id = get_agency_id_foreign_column()

    url = relationship("URL", back_populates="confirmed_agencies")
    agency = relationship("Agency", back_populates="confirmed_urls")

    __table_args__ = (
        UniqueConstraint("url_id", "agency_id", name="uq_confirmed_url_agency"),
    )
