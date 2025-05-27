from datetime import datetime

from pydantic import BaseModel

from src.collector_manager.enums import CollectorType
from src.core.enums import BatchStatus


class BatchStatusInfo(BaseModel):
    id: int
    date_generated: datetime
    strategy: CollectorType
    status: BatchStatus