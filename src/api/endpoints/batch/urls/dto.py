from pydantic import BaseModel

from src.db.models.instantiations.url.core.pydantic import URLInfo


class GetURLsByBatchResponse(BaseModel):
    urls: list[URLInfo]