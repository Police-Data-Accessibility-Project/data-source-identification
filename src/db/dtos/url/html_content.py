from src.db.models.impl.url.html.content.enums import HTMLContentType
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLHTMLContentInfo(BulkInsertableModel):
    url_id: int | None = None
    content_type: HTMLContentType
    content: str | list[str]

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URLHTMLContent