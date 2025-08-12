from src.db.models.impl.link.url_redirect_url.sqlalchemy import LinkURLRedirectURL
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkURLRedirectURLPydantic(BulkInsertableModel):
    source_url_id: int
    destination_url_id: int

    @classmethod
    def sa_model(cls) -> type[LinkURLRedirectURL]:
        return LinkURLRedirectURL

