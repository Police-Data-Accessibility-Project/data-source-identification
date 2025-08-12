from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLInsertModel(BulkInsertableModel):

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URL

    url: str
    collector_metadata: dict | None = None
    name: str | None = None
    status: URLStatus = URLStatus.PENDING
    record_type: RecordType | None = None
    source: URLSource