import pytest
from pydantic import BaseModel

from src.core.tasks.scheduled.impl.backlog.operator import PopulateBacklogSnapshotTaskOperator
from src.core.tasks.scheduled.impl.delete_logs.operator import DeleteOldLogsTaskOperator
from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.core.tasks.scheduled.impl.run_url_tasks.operator import RunURLTasksTaskOperator
from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase


class FlagTestParams(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    env_var: str
    operator: type[ScheduledTaskOperatorBase]

params: list[FlagTestParams] = [
    FlagTestParams(
        env_var="SYNC_AGENCIES_TASK_FLAG",
        operator=SyncAgenciesTaskOperator
    ),
    FlagTestParams(
        env_var="SYNC_DATA_SOURCES_TASK_FLAG",
        operator=SyncDataSourcesTaskOperator
    ),
    FlagTestParams(
        env_var="PUSH_TO_HUGGING_FACE_TASK_FLAG",
        operator=PushToHuggingFaceTaskOperator
    ),
    FlagTestParams(
        env_var="POPULATE_BACKLOG_SNAPSHOT_TASK_FLAG",
        operator=PopulateBacklogSnapshotTaskOperator
    ),
    FlagTestParams(
        env_var="DELETE_OLD_LOGS_TASK_FLAG",
        operator=DeleteOldLogsTaskOperator
    ),
    FlagTestParams(
        env_var="RUN_URL_TASKS_TASK_FLAG",
        operator=RunURLTasksTaskOperator
    )
]


@pytest.mark.asyncio
@pytest.mark.parametrize("flag_test_params", params)
async def test_flag_enabled(
    flag_test_params: FlagTestParams,
    monkeypatch,
    loader: ScheduledTaskOperatorLoader
):
    monkeypatch.setenv(flag_test_params.env_var, "0")
    entries: list[ScheduledTaskEntry] = await loader.load_entries()
    for entry in entries:
        if isinstance(entry.operator, flag_test_params.operator):
            assert not entry.enabled, f"Flag associated with env_var {flag_test_params.env_var} should be disabled"
