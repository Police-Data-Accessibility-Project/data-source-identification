from pydantic import Field

from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel


class URLWebMetadataPydantic(
    BulkInsertableModel,
    BulkUpsertableModel
):

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URLWebMetadata

    @classmethod
    def id_field(cls) -> str:
        return "url_id"

    url_id: int
    accessed: bool
    status_code: int | None = Field(le=999, ge=100)
    content_type: str | None
    error_message: str | None