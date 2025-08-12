from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class InsertURLForDataSourcesSyncParams(BulkInsertableModel):
    url: str
    name: str
    description: str | None
    status: URLStatus
    record_type: RecordType
    source: URLSource = URLSource.DATA_SOURCES

    @classmethod
    def sa_model(cls) -> type[URL]:
        return URL