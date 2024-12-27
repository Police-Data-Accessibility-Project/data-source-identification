from pydantic import BaseModel

from collector_manager.enums import CollectorType


class CollectorStartParams(BaseModel):
    collector_type: CollectorType
    config: dict
    batch_id: int = None
