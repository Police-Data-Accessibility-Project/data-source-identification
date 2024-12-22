from pydantic import BaseModel


class URLInfo(BaseModel):
    batch_id: int
    url: str
    url_metadata: dict
    outcome: str
