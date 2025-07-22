from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.templates import Base
from src.db.templates.upsert import UpsertModel
from src.db.models.instantiations.url.core.sqlalchemy import URL


class URLUpsertModel(UpsertModel):

    @property
    def id_field(self) -> str:
        return "id"

    @property
    def sa_model(self) -> type[Base]:
        return URL

    id: int
    url: str
    name: str
    description: str
    collector_metadata: dict | None = None
    outcome: URLStatus
    record_type: RecordType