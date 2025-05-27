from pydantic import BaseModel

from db.DTOs.URLInfo import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]