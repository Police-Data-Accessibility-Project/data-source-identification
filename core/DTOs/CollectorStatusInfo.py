from pydantic import BaseModel

from collector_manager.enums import CollectorType, CollectorStatus

class CollectorStatusInfo(BaseModel):
    batch_id: int
    collector_type: CollectorType
    status: CollectorStatus
