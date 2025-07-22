from pydantic import BaseModel

from src.db.dtos.url.core import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]