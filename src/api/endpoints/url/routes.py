from fastapi import APIRouter, Query, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.url.dtos.response import GetURLsResponseInfo
from src.core.core import AsyncCore
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

url_router = APIRouter(
    prefix="/url",
    tags=["URL"],
    responses={404: {"description": "Not found"}},
)

@url_router.get("")
async def get_urls(
        page: int = Query(
            description="The page number",
            default=1
        ),
        errors: bool = Query(
            description="Retrieve only URLs with errors",
            default=False
        ),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> GetURLsResponseInfo:
    result = await async_core.get_urls(page=page, errors=errors)
    return result
