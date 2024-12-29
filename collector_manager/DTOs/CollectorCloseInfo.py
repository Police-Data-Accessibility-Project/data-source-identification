from pydantic import BaseModel

from collector_manager.enums import CollectorType
from core.enums import BatchStatus


class CollectorCloseInfo(BaseModel):
    batch_id: int
    collector_type: CollectorType
    status: BatchStatus
    data: BaseModel = None
    message: str = None
    compute_time: float
