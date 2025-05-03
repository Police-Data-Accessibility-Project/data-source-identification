from typing import Optional

from pydantic import BaseModel, Field

from core.enums import RecordType


class ManualBatchInnerInputDTO(BaseModel):
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    collector_metadata: Optional[dict] = None
    record_type: Optional[RecordType] = None
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    supplying_entity: Optional[str] = None


class ManualBatchInputDTO(BaseModel):
    name: str
    entries: list[ManualBatchInnerInputDTO] = Field(
        min_length=1,
        max_length=1000
    )