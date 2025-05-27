from pydantic import BaseModel

from src.db.DTOs.DuplicateInfo import DuplicateInfo
from src.db.DTOs.URLMapping import URLMapping


class CollectionLifecycleInfo(BaseModel):
    batch_id: int
    url_id_mapping: list[URLMapping]
    duplicates: list[DuplicateInfo]
    message: str
