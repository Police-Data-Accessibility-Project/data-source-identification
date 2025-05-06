from fastapi import APIRouter
from fastapi.params import Query

from core.AsyncCore import AsyncCore
from core.DTOs.GetMetricsBacklogResponse import GetMetricsBacklogResponseDTO
from core.DTOs.GetMetricsBatchesAggregatedResponseDTO import GetMetricsBatchesAggregatedResponseDTO
from core.DTOs.GetMetricsBatchesBreakdownResponseDTO import GetMetricsBatchesBreakdownResponseDTO
from core.DTOs.GetMetricsURLsAggregatedResponseDTO import GetMetricsURLsAggregatedResponseDTO
from core.DTOs.GetMetricsURLsBreakdownPendingResponseDTO import GetMetricsURLsBreakdownPendingResponseDTO
from core.DTOs.GetMetricsURLsBreakdownSubmittedResponseDTO import GetMetricsURLsBreakdownSubmittedResponseDTO
from security_manager.SecurityManager import AccessInfo

metrics_router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


@metrics_router.get("/batches/aggregated")
async def get_batches_aggregated_metrics(
        core: AsyncCore,
        access_info: AccessInfo
) -> GetMetricsBatchesAggregatedResponseDTO:
    return await core.get_batches_aggregated_metrics()

@metrics_router.get("/batches/breakdown")
async def get_batches_breakdown_metrics(
        core: AsyncCore,
        access_info: AccessInfo,
        page: int = Query(
            description="The page number",
            default=1
        )
) -> GetMetricsBatchesBreakdownResponseDTO:
    return await core.get_batches_breakdown_metrics(page=page)

@metrics_router.get("/urls/aggregate")
async def get_urls_aggregated_metrics(
        core: AsyncCore,
        access_info: AccessInfo
) -> GetMetricsURLsAggregatedResponseDTO:
    return await core.get_urls_aggregated_metrics()

@metrics_router.get("/urls/breakdown/submitted")
async def get_urls_breakdown_submitted_metrics(
        core: AsyncCore,
        access_info: AccessInfo
) -> GetMetricsURLsBreakdownSubmittedResponseDTO:
    return await core.get_urls_breakdown_submitted_metrics()

@metrics_router.get("/urls/breakdown/pending")
async def get_urls_breakdown_pending_metrics(
        core: AsyncCore,
        access_info: AccessInfo
) -> GetMetricsURLsBreakdownPendingResponseDTO:
    return await core.get_urls_breakdown_pending_metrics()

@metrics_router.get("/backlog")
async def get_backlog_metrics(
        core: AsyncCore,
        access_info: AccessInfo
) -> GetMetricsBacklogResponseDTO:
    return await core.get_backlog_metrics()