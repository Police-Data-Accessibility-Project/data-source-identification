from pydantic import BaseModel


class BulkUpsertableModel(BaseModel):
    """Identifies a model that can be used for the bulk_upsert function in session_helper."""