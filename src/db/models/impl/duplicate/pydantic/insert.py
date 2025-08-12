from src.db.models.impl.duplicate.sqlalchemy import Duplicate
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class DuplicateInsertInfo(BulkInsertableModel):
    original_url_id: int
    batch_id: int

    @classmethod
    def sa_model(self) -> type[Duplicate]:
        return Duplicate