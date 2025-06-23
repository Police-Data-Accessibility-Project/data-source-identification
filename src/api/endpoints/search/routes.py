from fastapi import APIRouter, Query, Depends

from src.api.dependencies import get_async_core
from src.api.endpoints.search.dtos.response import SearchURLResponse
from src.core.core import AsyncCore
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

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