from fastapi import APIRouter
from fastapi.params import Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.collector.dtos.collector_start import CollectorStartInfo
from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.collectors.impl.auto_googler.dtos.input import AutoGooglerInputDTO
from src.collectors.impl.common_crawler.input import CommonCrawlerInputDTO
from src.collectors.impl.example.dtos.input import ExampleInputDTO
from src.collectors.enums import CollectorType
from src.core.core import AsyncCore
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo
from src.collectors.impl.ckan.dtos.input import CKANInputDTO
from src.collectors.impl.muckrock.collectors.all_foia.dto import MuckrockAllFOIARequestsCollectorInputDTO
from src.collectors.impl.muckrock.collectors.county.dto import MuckrockCountySearchCollectorInputDTO
from src.collectors.impl.muckrock.collectors.simple.dto import MuckrockSimpleSearchCollectorInputDTO

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

@collector_router.post("/manual")
async def upload_manual_collector(
        dto: ManualBatchInputDTO,
        core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> ManualBatchResponseDTO:
    """
    Uploads a manual "collector" with existing data
    """
    return await core.upload_manual_batch(
        dto=dto,
        user_id=access_info.user_id
    )