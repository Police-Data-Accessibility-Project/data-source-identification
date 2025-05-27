from pydantic import BaseModel

from db.DTOs.BatchInfo import BatchInfo


class GetBatchStatusResponse(BaseModel):
    results: list[BatchInfo]