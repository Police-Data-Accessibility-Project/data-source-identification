from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLCompressedHTMLPydantic(BulkInsertableModel):
    url_id: int
    compressed_html: bytes

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URLCompressedHTML