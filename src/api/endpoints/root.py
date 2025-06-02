from fastapi import APIRouter, Query, Depends

from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

root_router = APIRouter(prefix="", tags=["root"])

@root_router.get("/")
async def root(
    test: str = Query(description="A test parameter"),
    access_info: AccessInfo = Depends(get_access_info),
) -> dict[str, str]:
    """
    A simple root endpoint for testing and pinging
    """
    return {"message": "Hello World"}