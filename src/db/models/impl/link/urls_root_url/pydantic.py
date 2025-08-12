from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class LinkURLRootURLPydantic(BulkInsertableModel):

    url_id: int
    root_url_id: int

    @classmethod
    def sa_model(cls) -> type[LinkURLRootURL]:
        return LinkURLRootURL