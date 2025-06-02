from pydantic import BaseModel

from src.db.dtos.batch_info import BatchInfo


class GetBatchStatusResponse(BaseModel):
    results: list[BatchInfo]