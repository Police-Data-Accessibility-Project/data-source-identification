from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.data_sources import \
    TestDSURLSetupEntry
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.source_collector import \
    TestSCURLSetupEntry


class TestURLPostSetupRecord(BaseModel):
    """Stores a setup entry along with relevant database-generated ids"""
    url_id: int | None
    sc_setup_entry: TestSCURLSetupEntry | None
    ds_setup_entry: TestDSURLSetupEntry | None
    sc_agency_ids: list[int] | None
    ds_agency_ids: list[int] | None
    ds_response_info: DataSourcesSyncResponseInnerInfo | None
    final_url_status: URLStatus

    @property
    def data_sources_id(self) -> int | None:
        if self.ds_setup_entry is None:
            return None
        return self.ds_setup_entry.id

    @property
    def final_record_type(self) -> RecordType:
        if self.ds_setup_entry is not None:
            return self.ds_setup_entry.record_type
        return self.sc_setup_entry.record_type

    @property
    def final_name(self) -> str:
        if self.ds_setup_entry is not None:
            return self.ds_setup_entry.name
        return self.sc_setup_entry.name

    @property
    def final_description(self) -> str:
        if self.ds_setup_entry is not None:
            return self.ds_setup_entry.description
        return self.sc_setup_entry.description

    @property
    def final_agency_ids(self) -> list[int] | None:
        if self.ds_setup_entry is not None:
            return self.ds_agency_ids
        return self.sc_agency_ids