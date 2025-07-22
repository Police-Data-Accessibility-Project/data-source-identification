from datetime import datetime

from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.templates import Base
from src.db.templates.upsert import UpsertModel


class AgencyUpsertModel(UpsertModel):

    @property
    def id_field(self) -> str:
        return "agency_id"

    @property
    def sa_model(self) -> type[Base]:
        return Agency

    agency_id: int
    name: str
    state: str | None
    county: str | None
    locality: str | None
    ds_last_updated_at: datetime
