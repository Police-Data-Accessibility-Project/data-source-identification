from pydantic import BaseModel


class BulkDeletableModel(BaseModel):
    """Identifies a model that can be used for the bulk_delete function in session_helper."""

