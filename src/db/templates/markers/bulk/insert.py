from pydantic import BaseModel


class BulkInsertableModel(BaseModel):
    """Identifies a model that can be used for the bulk_insert function in session_helper."""
