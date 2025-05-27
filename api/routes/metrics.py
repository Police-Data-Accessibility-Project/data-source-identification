from fastapi import APIRouter
from fastapi.params import Query, Depends

from api.dependencies import get_async_core
from src.core.AsyncCore import AsyncCore
from src.core.DTOs.GetMetricsBacklogResponse import GetMetricsBacklogResponseDTO
from src.core.DTOs.GetMetricsBatchesAggregatedResponseDTO import GetMetricsBatchesAggregatedResponseDTO
from src.core.DTOs.GetMetricsBatchesBreakdownResponseDTO import GetMetricsBatchesBreakdownResponseDTO
from src.core.DTOs.GetMetricsURLsAggregatedResponseDTO import GetMetricsURLsAggregatedResponseDTO
from src.core.DTOs.GetMetricsURLsBreakdownPendingResponseDTO import GetMetricsURLsBreakdownPendingResponseDTO
from src.core.DTOs.GetMetricsURLsBreakdownSubmittedResponseDTO import GetMetricsURLsBreakdownSubmittedResponseDTO
from src.security_manager.SecurityManager import AccessInfo, get_access_info

metrics_router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


@metrics_router.get("/batches/aggregated")
async def get_batches_aggregated_metrics(
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetMetricsBatchesAggregatedResponseDTO:
    return await core.get_batches_aggregated_metrics()

@metrics_router.get("/batches/breakdown")
async def get_batches_breakdown_metrics(
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
        page: int = Query(
            description="The page number",
            default=1
        )
) -> GetMetricsBatchesBreakdownResponseDTO:
    return await core.get_batches_breakdown_metrics(page=page)

@metrics_router.get("/urls/aggregate")
async def get_urls_aggregated_metrics(
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetMetricsURLsAggregatedResponseDTO:
    return await core.get_urls_aggregated_metrics()

@metrics_router.get("/urls/breakdown/submitted")
async def get_urls_breakdown_submitted_metrics(
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetMetricsURLsBreakdownSubmittedResponseDTO:
    return await core.get_urls_breakdown_submitted_metrics()

@metrics_router.get("/urls/breakdown/pending")
async def get_urls_breakdown_pending_metrics(
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetMetricsURLsBreakdownPendingResponseDTO:
    return await core.get_urls_breakdown_pending_metrics()

@metrics_router.get("/backlog")
async def get_backlog_metrics(
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetMetricsBacklogResponseDTO:
    return await core.get_backlog_metrics()