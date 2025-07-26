from pydantic import BaseModel


class BulkUpdatableModel(BaseModel):
    """Identifies a model that can be used for the bulk_update function in session_helper."""
