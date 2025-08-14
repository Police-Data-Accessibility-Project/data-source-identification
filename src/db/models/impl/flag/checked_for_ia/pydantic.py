from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class FlagURLCheckedForInternetArchivesPydantic(BulkInsertableModel):
    url_id: int

    @classmethod
    def sa_model(cls) -> type[FlagURLCheckedForInternetArchives]:
        return FlagURLCheckedForInternetArchives