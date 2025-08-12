from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.templates.markers.bulk.update import BulkUpdatableModel


class UpdateURLForDataSourcesSyncParams(BulkUpdatableModel):

    @classmethod
    def id_field(cls) -> str:
        return "id"

    @classmethod
    def sa_model(cls) -> type[URL]:
        return URL

    id: int
    name: str
    description: str | None
    status: URLStatus
    record_type: RecordType
