from pydantic import BaseModel


class ManualBatchOutputDTO(BaseModel):
    batch_id: int
    urls: list[int]