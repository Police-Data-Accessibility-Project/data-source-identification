from pydantic import BaseModel

from src.db.models.impl.url.core.pydantic.info import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]