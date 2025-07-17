from pydantic import BaseModel

from src.db.dtos.url.insert import InsertURLsInfo


class AnnotationSetupInfo(BaseModel):
    batch_id: int
    insert_urls_info: InsertURLsInfo
