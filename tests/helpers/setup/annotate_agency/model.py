from pydantic import BaseModel


class AnnotateAgencySetupInfo(BaseModel):
    batch_id: int
    url_ids: list[int]
