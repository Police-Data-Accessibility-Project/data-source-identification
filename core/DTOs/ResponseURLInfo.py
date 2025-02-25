from pydantic import BaseModel


class ResponseURLInfo(BaseModel):
    url: str
    url_id: int