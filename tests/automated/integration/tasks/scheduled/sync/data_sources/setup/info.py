from pydantic import BaseModel

from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo


class TestDataSourcesSyncSetupInfo(BaseModel):

    class Config:
        allow_arbitrary_types = True

    preexisting_urls: list[URL]
    preexisting_urls_ids: list[int]
    first_call_response: DataSourcesSyncResponseInfo
    second_call_response: DataSourcesSyncResponseInfo
    third_call_response: DataSourcesSyncResponseInfo