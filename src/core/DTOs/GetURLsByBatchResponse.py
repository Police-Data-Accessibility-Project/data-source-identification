from pydantic import BaseModel

from src.db.DTOs.URLInfo import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]