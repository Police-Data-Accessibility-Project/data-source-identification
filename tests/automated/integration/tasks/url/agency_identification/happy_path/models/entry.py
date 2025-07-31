from pydantic import BaseModel

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.subtasks.base import AgencyIdentificationSubtaskBase


class TestAgencyIdentificationURLSetupEntry(BaseModel):
    collector_type: CollectorType | None
    url_status: URLStatus
    expected_subtask: AgencyIdentificationSubtaskBase


