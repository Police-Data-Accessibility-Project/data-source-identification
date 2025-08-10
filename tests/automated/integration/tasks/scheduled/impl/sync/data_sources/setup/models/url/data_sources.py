from pydantic import BaseModel

from src.core.enums import RecordType
from src.external.pdap.enums import DataSourcesURLStatus, ApprovalStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.enums import AgencyAssigned, SyncResponseOrder


class TestDSURLSetupEntry(BaseModel):
    """Represents URL previously existing in DS DB.

    These values should overwrite any SC values
    """
    id: int  # ID of URL in DS App
    name: str
    description: str | None
    url_status: DataSourcesURLStatus
    approval_status: ApprovalStatus
    record_type: RecordType
    agencies_assigned: list[AgencyAssigned]
    sync_response_order: SyncResponseOrder
