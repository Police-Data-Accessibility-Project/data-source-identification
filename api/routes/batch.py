from typing import Optional

from fastapi import Path, APIRouter
from fastapi.params import Query, Depends

from api.dependencies import get_core
from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.enums import CollectorType
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus

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
        core: SourceCollectorCore = Depends(get_core)
) -> GetBatchStatusResponse:
    """
    Get the status of recent batches
    """
    return core.get_batch_statuses(collector_type=collector_type, status=status, limit=limit)


@batch_router.get("/{batch_id}")
def get_batch_info(
        batch_id: int = Path(description="The batch id"),
        core: SourceCollectorCore = Depends(get_core)
) -> BatchInfo:
    return core.get_batch_info(batch_id)