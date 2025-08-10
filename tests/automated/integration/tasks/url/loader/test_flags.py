import pytest
from pydantic import BaseModel

from src.core.tasks.url.models.entry import URLTaskEntry
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.auto_relevant.core import URLAutoRelevantTaskOperator
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.duplicate.core import URLDuplicateTaskOperator
from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.misc_metadata.core import URLMiscellaneousMetadataTaskOperator
from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from src.core.tasks.url.operators.probe_404.core import URL404ProbeTaskOperator
from src.core.tasks.url.operators.record_type.core import URLRecordTypeTaskOperator
from src.core.tasks.url.operators.submit_approved.core import SubmitApprovedURLTaskOperator


class FlagTestParams(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    env_var: str
    operator: type[URLTaskOperatorBase]

params = [
    FlagTestParams(
        env_var="URL_HTML_TASK_FLAG",
        operator=URLHTMLTaskOperator
    ),
    FlagTestParams(
        env_var="URL_RECORD_TYPE_TASK_FLAG",
        operator=URLRecordTypeTaskOperator
    ),
    FlagTestParams(
        env_var="URL_AGENCY_IDENTIFICATION_TASK_FLAG",
        operator=AgencyIdentificationTaskOperator
    ),
    FlagTestParams(
        env_var="URL_SUBMIT_APPROVED_TASK_FLAG",
        operator=SubmitApprovedURLTaskOperator
    ),
    FlagTestParams(
        env_var="URL_DUPLICATE_TASK_FLAG",
        operator=URLDuplicateTaskOperator
    ),
    FlagTestParams(
        env_var="URL_MISC_METADATA_TASK_FLAG",
        operator=URLMiscellaneousMetadataTaskOperator
    ),
    FlagTestParams(
        env_var="URL_404_PROBE_TASK_FLAG",
        operator=URL404ProbeTaskOperator
    ),
    FlagTestParams(
        env_var="URL_AUTO_RELEVANCE_TASK_FLAG",
        operator=URLAutoRelevantTaskOperator
    ),
    FlagTestParams(
        env_var="URL_PROBE_TASK_FLAG",
        operator=URLProbeTaskOperator
    ),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("flag_test_params", params)
async def test_flag_enabled(
    flag_test_params: FlagTestParams,
    monkeypatch,
    loader
):
    monkeypatch.setenv(flag_test_params.env_var, "0")
    entries: list[URLTaskEntry] = await loader.get_task_operators()
    for entry in entries:
        if isinstance(entry.operator, flag_test_params.operator):
            assert not entry.enabled, f"Flag associated with env_var {flag_test_params.env_var} should be disabled"
