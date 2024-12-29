from fastapi import APIRouter, Query

root_router = APIRouter(prefix="", tags=["root"])

@root_router.get("/")
async def root(test: str = Query(description="A test parameter")) -> dict[str, str]:
    return {"message": "Hello World"}