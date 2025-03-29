from typing import Optional

from pydantic import BaseModel

from collector_manager.enums import CollectorType


class URLMiscellaneousMetadataTDO(BaseModel):
    url_id: int
    collector_metadata: dict
    collector_type: CollectorType
    name: Optional[str] = None
    description: Optional[str] = None
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    supplying_entity: Optional[str] = None
