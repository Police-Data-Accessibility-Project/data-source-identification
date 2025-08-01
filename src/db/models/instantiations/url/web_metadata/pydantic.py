from src.db.models.instantiations.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.models.templates import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLWebMetadataPydantic(BulkInsertableModel):

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URLWebMetadata


    url_id: int
    accessed: bool
    status_code: int | None
    content_type: str | None
    error_message: str | None