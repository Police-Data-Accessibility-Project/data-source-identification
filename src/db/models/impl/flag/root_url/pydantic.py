from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class FlagRootURLPydantic(BulkInsertableModel):

    url_id: int

    @classmethod
    def sa_model(cls) -> type[FlagRootURL]:
        return FlagRootURL