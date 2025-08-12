from typing import Optional

from pydantic import BaseModel

from src.collectors.enums import CollectorType


class AgencyIdentificationTDO(BaseModel):
    url_id: int
    collector_metadata: dict | None = None
    collector_type: CollectorType | None
