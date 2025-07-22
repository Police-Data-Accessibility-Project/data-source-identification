from pydantic import BaseModel

from src.db.models.instantiations.url.core.pydantic.info import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]