from pydantic import BaseModel


class RawHTMLInfo(BaseModel):
    url_id: int
    html: str