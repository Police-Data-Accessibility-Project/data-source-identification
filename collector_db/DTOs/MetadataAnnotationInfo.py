from datetime import datetime

from pydantic import BaseModel


class MetadataAnnotationInfo(BaseModel):
    id: int
    user_id: int
    metadata_id: int
    value: str
    created_at: datetime
