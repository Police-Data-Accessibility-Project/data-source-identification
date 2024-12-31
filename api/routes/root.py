from fastapi import APIRouter, Query, Depends

from security_manager.SecurityManager import AccessInfo, get_access_info

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