from src.db.templates.markers.bulk.delete import BulkDeletableModel
from src.db.templates.markers.bulk.insert import BulkInsertableModel
from src.db.templates.markers.bulk.update import BulkUpdatableModel
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel

BulkActionType = (
    BulkInsertableModel | BulkUpdatableModel | BulkDeletableModel | BulkUpsertableModel
)
