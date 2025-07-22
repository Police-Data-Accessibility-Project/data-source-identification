from pydantic import BaseModel

from src.core.tasks.scheduled.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo


class TestDataSourcesSyncSetupInfo(BaseModel):

    class Config:
        allow_arbitrary_types = True

    operator: SyncDataSourcesTaskOperator
    db_client: AsyncDatabaseClient
    preexisting_urls: list[URL]
    preexisting_urls_ids: list[int]
    first_call_response: DataSourcesSyncResponseInfo
    second_call_response: DataSourcesSyncResponseInfo
    third_call_response: DataSourcesSyncResponseInfo

    @property
    def data_sources_sync_response(self) -> list[DataSourcesSyncResponseInfo]:
        return [
            self.first_call_response,
            self.second_call_response,
            self.third_call_response
        ]