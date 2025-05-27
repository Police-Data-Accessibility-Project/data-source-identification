from typing import Optional

from pydantic import BaseModel

from src.collector_manager.enums import CollectorType


class AgencyIdentificationTDO(BaseModel):
    url_id: int
    collector_metadata: Optional[dict] = None
    collector_type: CollectorType
