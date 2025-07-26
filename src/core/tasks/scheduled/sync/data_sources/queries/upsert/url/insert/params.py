from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class InsertURLForDataSourcesSyncParams(BulkInsertableModel):
    url: str
    name: str
    description: str | None
    outcome: URLStatus
    record_type: RecordType

    @classmethod
    def sa_model(cls) -> type[URL]:
        return URL