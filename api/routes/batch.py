from typing import Optional

from fastapi import Path, APIRouter
from fastapi.params import Query, Depends

from api.dependencies import get_core
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.enums import CollectorType
from core.DTOs.GetBatchLogsResponse import GetBatchLogsResponse
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.DTOs.GetDuplicatesByBatchResponse import GetDuplicatesByBatchResponse
from core.DTOs.GetURLsByBatchResponse import GetURLsByBatchResponse
from core.DTOs.MessageResponse import MessageResponse
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus
from security_manager.SecurityManager import AccessInfo, get_access_info

batch_router = APIRouter(
    prefix="/batch",
    tags=["Batch"],
    responses={404: {"description": "Not found"}},
)


@batch_router.get("")
def get_batch_status(
        collector_type: Optional[CollectorType] = Query(
            description="Filter by collector type",
            default=None
        ),
        status: Optional[BatchStatus] = Query(
            description="Filter by status",
            default=None
        ),
        limit: int = Query(
            description="The number of results to return",
            default=10
        ),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetBatchStatusResponse:
    """
    Get the status of recent batches
    """
    return core.get_batch_statuses(collector_type=collector_type, status=status, limit=limit)


@batch_router.get("/{batch_id}")
def get_batch_info(
        batch_id: int = Path(description="The batch id"),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> BatchInfo:
    return core.get_batch_info(batch_id)

@batch_router.get("/{batch_id}/urls")
def get_urls_by_batch(
        batch_id: int = Path(description="The batch id"),
        page: int = Query(
            description="The page number",
            default=1
        ),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetURLsByBatchResponse:
    return core.get_urls_by_batch(batch_id, page=page)

@batch_router.get("/{batch_id}/duplicates")
def get_duplicates_by_batch(
        batch_id: int = Path(description="The batch id"),
        page: int = Query(
            description="The page number",
            default=1
        ),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetDuplicatesByBatchResponse:
    return core.get_duplicate_urls_by_batch(batch_id, page=page)

@batch_router.get("/{batch_id}/logs")
def get_batch_logs(
        batch_id: int = Path(description="The batch id"),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetBatchLogsResponse:
    """
    Retrieve the logs for a recent batch.
    Note that for later batches, the logs may not be available.
    """
    return core.get_batch_logs(batch_id)

@batch_router.post("/{batch_id}/abort")
def abort_batch(
        batch_id: int = Path(description="The batch id"),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> MessageResponse:
    return core.abort_batch(batch_id)