from fastapi import APIRouter, Query, Depends

from api.dependencies import get_async_core
from core.AsyncCore import AsyncCore
from core.DTOs.SearchURLResponse import SearchURLResponse
from security_manager.SecurityManager import get_access_info, AccessInfo

search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.get("/url")
async def search_url(
    url: str = Query(description="The URL to search for"),
    access_info: AccessInfo = Depends(get_access_info),
    async_core: AsyncCore = Depends(get_async_core),
) -> SearchURLResponse:
    """
    Search for a URL in the database
    """
    return await async_core.search_for_url(url)