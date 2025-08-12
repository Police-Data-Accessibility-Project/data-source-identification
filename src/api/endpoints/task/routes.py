from typing import Optional

from fastapi import APIRouter, Depends, Query, Path

from src.api.dependencies import get_async_core
from src.api.endpoints.task.by_id.dto import TaskInfo
from src.api.endpoints.task.dtos.get.tasks import GetTasksResponse
from src.api.endpoints.task.dtos.get.task_status import GetTaskStatusResponseInfo
from src.db.enums import TaskType
from src.core.core import AsyncCore
from src.core.enums import BatchStatus
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

task_router = APIRouter(
    prefix="/task",
    tags=["Task"],
    responses={404: {"description": "Not found"}},
)


@task_router.get("")
async def get_tasks(
        page: int = Query(
            description="The page number",
            default=1
        ),
        task_status: BatchStatus | None = Query(
            description="Filter by task status",
            default=None
        ),
        task_type: TaskType | None = Query(
            description="Filter by task type",
            default=None
        ),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetTasksResponse:
    return await async_core.get_tasks(
        page=page,
        task_type=task_type,
        task_status=task_status
    )

@task_router.get("/status")
async def get_task_status(
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetTaskStatusResponseInfo:
    return await async_core.get_current_task_status()

@task_router.get("/{task_id}")
async def get_task_info(
        task_id: int = Path(description="The task id"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> TaskInfo:
    return await async_core.get_task_info(task_id)


