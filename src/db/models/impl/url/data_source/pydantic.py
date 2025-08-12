from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLDataSourcePydantic(BulkInsertableModel):
    data_source_id: int
    url_id: int

    @classmethod
    def sa_model(cls) -> type[URLDataSource]:
        return URLDataSource