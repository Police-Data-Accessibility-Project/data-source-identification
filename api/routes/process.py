from fastapi import Depends

from security_manager.SecurityManager import AccessInfo, get_access_info

process_router = APIRouter(
    prefix="/process",
    tags=["Process"],
    responses={404: {"description": "Not found"}},
)

@process_router.get("")
def process(
    access_info: AccessInfo = Depends(get_access_info)
):

