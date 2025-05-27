from fastapi import APIRouter, Query, Depends

from api.dependencies import get_async_core
from src.core.AsyncCore import AsyncCore
from src.core.DTOs.GetURLsResponseInfo import GetURLsResponseInfo
from src.security_manager.SecurityManager import AccessInfo, get_access_info

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
