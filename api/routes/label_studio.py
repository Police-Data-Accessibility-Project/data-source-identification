from fastapi import APIRouter, Path, Depends

from api.dependencies import get_core
from core.DTOs.LabelStudioExportResponseInfo import LabelStudioExportResponseInfo
from core.SourceCollectorCore import SourceCollectorCore
from security_manager.SecurityManager import get_access_info, AccessInfo

label_studio_router = APIRouter(
    prefix="/label-studio",
    tags=["Label Studio"],
    responses={404: {"description": "Not found"}},
)

# TODO: Delete
@label_studio_router.post("/export-batch/{batch_id}")
def export_batch_to_label_studio(
        batch_id: int = Path(description="The batch id"),
        core: SourceCollectorCore = Depends(get_core),
        access_info: AccessInfo = Depends(get_access_info),
) -> LabelStudioExportResponseInfo:
    """
    Export a batch of URLs to Label Studio
    """
    return core.export_batch_to_label_studio(batch_id)