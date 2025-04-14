from fastapi import APIRouter
from fastapi.params import Depends

from api.dependencies import get_async_core
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType
from core.AsyncCore import AsyncCore
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from security_manager.SecurityManager import AccessInfo, get_access_info
from source_collectors.auto_googler.DTOs import AutoGooglerInputDTO
from source_collectors.ckan.DTOs import CKANInputDTO
from source_collectors.common_crawler.DTOs import CommonCrawlerInputDTO
from source_collectors.muckrock.DTOs import MuckrockCountySearchCollectorInputDTO, \
    MuckrockAllFOIARequestsCollectorInputDTO, MuckrockSimpleSearchCollectorInputDTO

collector_router = APIRouter(
    prefix="/collector",
    tags=["Collector"],
    responses={404: {"description": "Not found"}},
)

@collector_router.post("/example")
async def start_example_collector(
        dto: ExampleInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the example collector
    """
    return await core.initiate_collector(
        collector_type=CollectorType.EXAMPLE,
        dto=dto,
        user_id=access_info.user_id
    )

@collector_router.post("/ckan")
async def start_ckan_collector(
        dto: CKANInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the ckan collector
    """
    return await core.initiate_collector(
        collector_type=CollectorType.CKAN,
        dto=dto,
        user_id=access_info.user_id
    )

@collector_router.post("/common-crawler")
async def start_common_crawler_collector(
        dto: CommonCrawlerInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the common crawler collector
    """
    return await core.initiate_collector(
        collector_type=CollectorType.COMMON_CRAWLER,
        dto=dto,
        user_id=access_info.user_id
    )

@collector_router.post("/auto-googler")
async def start_auto_googler_collector(
        dto: AutoGooglerInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the auto googler collector
    """
    return await core.initiate_collector(
        collector_type=CollectorType.AUTO_GOOGLER,
        dto=dto,
        user_id=access_info.user_id
    )

@collector_router.post("/muckrock-simple")
async def start_muckrock_collector(
        dto: MuckrockSimpleSearchCollectorInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the muckrock collector
    """
    return await core.initiate_collector(
        collector_type=CollectorType.MUCKROCK_SIMPLE_SEARCH,
        dto=dto,
        user_id=access_info.user_id
    )

@collector_router.post("/muckrock-county")
async def start_muckrock_county_collector(
        dto: MuckrockCountySearchCollectorInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the muckrock county level collector
    """
    return await core.initiate_collector(
        collector_type=CollectorType.MUCKROCK_COUNTY_SEARCH,
        dto=dto,
        user_id=access_info.user_id
    )

@collector_router.post("/muckrock-all")
async def start_muckrock_all_foia_collector(
        dto: MuckrockAllFOIARequestsCollectorInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> CollectorStartInfo:
    """
    Start the muckrock collector for all FOIA requests
    """
    return await core.initiate_collector(
        collector_type=CollectorType.MUCKROCK_ALL_SEARCH,
        dto=dto,
        user_id=access_info.user_id
    )