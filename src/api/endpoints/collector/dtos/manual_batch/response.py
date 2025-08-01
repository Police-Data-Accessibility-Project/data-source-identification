from pydantic import BaseModel


class ManualBatchResponseDTO(BaseModel):
    batch_id: int
    urls: list[int]
    duplicate_urls: list[str]