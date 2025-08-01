from pydantic import BaseModel


class URLMapping(BaseModel):
    """Mapping between url and url_id."""
    url: str
    url_id: int
