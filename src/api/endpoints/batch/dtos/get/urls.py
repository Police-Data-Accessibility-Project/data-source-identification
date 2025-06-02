from pydantic import BaseModel

from src.db.dtos.url_info import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]