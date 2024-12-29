from pydantic import BaseModel

from core.DTOs.BatchStatusInfo import BatchStatusInfo


class GetBatchStatusResponse(BaseModel):
    results: list[BatchStatusInfo]