from pydantic import BaseModel

from src.api.endpoints.batch.dtos.get.summaries.summary import BatchSummary


class GetBatchSummariesResponse(BaseModel):
    results: list[BatchSummary]
