from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.enums import AgencyAssigned


class TestSCURLSetupEntry(BaseModel):
    """Represents URL previously existing in SC DB.

    These values should be overridden by any DS values
    """
    name: str
    description: str
    record_type: RecordType | None
    url_status: URLStatus
    agencies_assigned: list[AgencyAssigned]
