from pydantic import BaseModel


class TestAsyncCoreSetupInfo(BaseModel):
    batch_id: int
    url_ids: list[int]
    task_id: int


