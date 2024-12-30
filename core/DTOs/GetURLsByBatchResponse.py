from pydantic import BaseModel

from collector_db.DTOs.URLInfo import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]