from typing import Optional

from pydantic import BaseModel, Field

from src.core.enums import RecordType


class ManualBatchInnerInputDTO(BaseModel):
    url: str
    name: str | None = None
    description: str | None = None
    collector_metadata: dict | None = None
    record_type: RecordType | None = None
    record_formats: list[str] | None = None
    data_portal_type: str | None = None
    supplying_entity: str | None = None


class ManualBatchInputDTO(BaseModel):
    name: str
    entries: list[ManualBatchInnerInputDTO] = Field(
        min_length=1,
        max_length=1000
    )