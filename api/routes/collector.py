from typing import Optional

from fastapi import APIRouter, Query
from fastapi.params import Depends

from api.dependencies import get_core
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.SourceCollectorCore import SourceCollectorCore
from security_manager.SecurityManager import AccessInfo, get_access_info

collector_router = APIRouter(
    prefix="/collector",
    tags=["Collector"],
    responses={404: {"description": "Not found"}},
)

@collector_router.post("/example")
async def start_example_collector(
        dto: ExampleInputDTO,
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the example collector
    """
    return core.initiate_collector(
        collector_type=CollectorType.EXAMPLE,
        dto=dto
    )