from pydantic import BaseModel


class URLRelevancyInfo(BaseModel):
    url_id: int
    relevant: bool