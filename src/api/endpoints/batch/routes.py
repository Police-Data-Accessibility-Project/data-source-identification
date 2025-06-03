from typing import Optional

from fastapi import Path, APIRouter
from fastapi.params import Query, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.batch.dtos.get.duplicates import GetDuplicatesByBatchResponse
from src.api.endpoints.batch.dtos.get.logs import GetBatchLogsResponse
from src.api.endpoints.batch.dtos.get.summaries import GetBatchSummariesResponse
from src.api.endpoints.batch.dtos.get.urls import GetURLsByBatchResponse
from src.api.endpoints.batch.dtos.post.abort import MessageResponse
from src.db.dtos.batch_info import BatchInfo
from src.collectors.enums import CollectorType
from src.core.core import AsyncCore
from src.core.enums import BatchStatus
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

batch_router = APIRouter(
    prefix="/batch",
    tags=["Batch"],
    responses={404: {"description": "Not found"}},
)


@batch_router.get("")
async def get_batch_status(
        collector_type: Optional[CollectorType] = Query(
            description="Filter by collector type",
            default=None
        ),
        status: Optional[BatchStatus] = Query(
            description="Filter by status",
            default=None
        ),
        has_pending_urls: Optional[bool] = Query(
            description="Filter by whether the batch has pending URLs",
            default=None
        ),
        page: int = Query(
            description="The page number",
            default=1
        ),
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetBatchSummariesResponse:
    """
    Get the status of recent batches
    """
    return await core.get_batch_statuses(
        collector_type=collector_type,
        status=status,
        has_pending_urls=has_pending_urls,
        page=page
    )


@batch_router.get("/{batch_id}")
async def get_batch_info(
        batch_id: int = Path(description="The batch id"),
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> BatchInfo:
    result = await core.get_batch_info(batch_id)
    return result

@batch_router.get("/{batch_id}/urls")
async def get_urls_by_batch(
        batch_id: int = Path(description="The batch id"),
        page: int = Query(
            description="The page number",
            default=1
        ),
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetURLsByBatchResponse:
    return await core.get_urls_by_batch(batch_id, page=page)

@batch_router.get("/{batch_id}/duplicates")
async def get_duplicates_by_batch(
        batch_id: int = Path(description="The batch id"),
        page: int = Query(
            description="The page number",
            default=1
        ),
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetDuplicatesByBatchResponse:
    return await core.get_duplicate_urls_by_batch(batch_id, page=page)

@batch_router.get("/{batch_id}/logs")
async def get_batch_logs(
        batch_id: int = Path(description="The batch id"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetBatchLogsResponse:
    """
    Retrieve the logs for a recent batch.
    Note that for later batches, the logs may not be available.
    """
    return await async_core.get_batch_logs(batch_id)

@batch_router.post("/{batch_id}/abort")
async def abort_batch(
        batch_id: int = Path(description="The batch id"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> MessageResponse:
    return await async_core.abort_batch(batch_id)