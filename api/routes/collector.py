from typing import Optional

from fastapi import APIRouter, Query
from fastapi.params import Depends

from api.dependencies import get_core
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.DTOs.GetStatusResponse import GetStatusResponse
from core.SourceCollectorCore import SourceCollectorCore

collector_router = APIRouter(
    prefix="/collector",
    tags=["Collector"],
    responses={404: {"description": "Not found"}},
)

@collector_router.get("/status")
async def get_status(
        batch_id: Optional[int] = Query(
            description="The collector id", default=None
        ),
        core: SourceCollectorCore = Depends(get_core)
) -> GetStatusResponse:
    return GetStatusResponse(
        batch_status=core.get_status(batch_id=batch_id)
    )



@collector_router.post("/example")
async def start_example_collector(
        dto: ExampleInputDTO,
        core: SourceCollectorCore = Depends(get_core)
) -> CollectorStartInfo:
    """
    Start the example collector
    """
    return core.initiate_collector(
        collector_type=CollectorType.EXAMPLE,
        dto=dto
    )