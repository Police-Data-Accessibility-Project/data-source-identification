from datetime import datetime

from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel


class AgencyUpsertModel(BulkUpsertableModel):

    @classmethod
    def id_field(cls) -> str:
        return "agency_id"

    @classmethod
    def sa_model(cls) -> type[Base]:
        return Agency

    agency_id: int
    name: str
    state: str | None
    county: str | None
    locality: str | None
