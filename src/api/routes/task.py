from typing import Optional

from fastapi import APIRouter, Depends, Query, Path

from src.api.dependencies import get_async_core
from src.db.DTOs.GetTaskStatusResponseInfo import GetTaskStatusResponseInfo
from src.db.DTOs.TaskInfo import TaskInfo
from src.db.enums import TaskType
from src.core.AsyncCore import AsyncCore
from src.core.enums import BatchStatus
from src.security_manager.SecurityManager import AccessInfo, get_access_info

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
        task_status: Optional[BatchStatus] = Query(
            description="Filter by task status",
            default=None
        ),
        task_type: Optional[TaskType] = Query(
            description="Filter by task type",
            default=None
        ),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
):
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


