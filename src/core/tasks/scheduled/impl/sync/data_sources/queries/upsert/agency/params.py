from pydantic import BaseModel


class UpdateLinkURLAgencyForDataSourcesSyncParams(BaseModel):
    url_id: int
    new_agency_ids: list[int]
    old_agency_ids: list[int]
