from pydantic import BaseModel

class URLDataSyncInfo(BaseModel):
    url: str
    url_id: int
    agency_ids: list[int]

class LookupURLForDataSourcesSyncResponse(BaseModel):
    data_source_id: int | None
    url_info: URLDataSyncInfo | None
