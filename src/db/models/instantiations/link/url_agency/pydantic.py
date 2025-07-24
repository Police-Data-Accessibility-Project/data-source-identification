from pydantic import BaseModel


class LinkURLAgencyUpsertModel(BaseModel):
    url_id: int
    agency_ids: list[int]