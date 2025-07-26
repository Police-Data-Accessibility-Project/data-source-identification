from datetime import datetime

from pydantic import BaseModel

from src.core.enums import RecordType
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus


class DataSourcesSyncResponseInnerInfo(BaseModel):
    id: int
    url: str
    name: str
    description: str | None
    record_type: RecordType
    agency_ids: list[int]
    approval_status: ApprovalStatus
    url_status: DataSourcesURLStatus
    updated_at: datetime

class DataSourcesSyncResponseInfo(BaseModel):
    data_sources: list[DataSourcesSyncResponseInnerInfo]