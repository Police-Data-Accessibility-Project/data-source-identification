from src.db.models.impl.url.ia_metadata.sqlalchemy import URLInternetArchivesMetadata
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLInternetArchiveMetadataPydantic(BulkInsertableModel):

    url_id: int
    archive_url: str
    digest: str
    length: int

    @classmethod
    def sa_model(cls) -> type[URLInternetArchivesMetadata]:
        return URLInternetArchivesMetadata
