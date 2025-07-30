from pydantic import BaseModel


class BatchURLCreationInfo(BaseModel):
    batch_id: int
    url_ids: list[int]
    urls: list[str]
