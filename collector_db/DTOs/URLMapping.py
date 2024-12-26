from pydantic import BaseModel


class URLMapping(BaseModel):
    url: str
    url_id: int
