from pydantic import BaseModel

from collector_db.DTOs.BatchInfo import BatchInfo


class GetBatchStatusResponse(BaseModel):
    results: list[BatchInfo]