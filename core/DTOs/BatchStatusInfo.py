from datetime import datetime

from pydantic import BaseModel

from collector_manager.enums import CollectorType
from core.enums import BatchStatus


class BatchStatusInfo(BaseModel):
    id: int
    date_generated: datetime
    strategy: CollectorType
    status: BatchStatus