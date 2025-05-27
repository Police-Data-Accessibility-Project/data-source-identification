from pydantic import BaseModel

from src.collector_manager import CollectorType


class CollectorStartParams(BaseModel):
    collector_type: CollectorType
    config: dict
    batch_id: int = None
