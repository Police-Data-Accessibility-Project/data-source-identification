import datetime
from typing import Optional

from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource

class GetURLsResponseErrorInfo(BaseModel):
    id: int
    error: str
    updated_at: datetime.datetime

class GetURLsResponseMetadataInfo(BaseModel):
    id: int
    attribute: URLMetadataAttributeType
    value: str
    validation_status: ValidationStatus
    validation_source: ValidationSource
    created_at: datetime.datetime
    updated_at: datetime.datetime

class GetURLsResponseInnerInfo(BaseModel):
    id: int
    batch_id: int | None
    url: str
    status: URLStatus
    collector_metadata: Optional[dict]
    updated_at: datetime.datetime
    created_at: datetime.datetime
    errors: list[GetURLsResponseErrorInfo]

class GetURLsResponseInfo(BaseModel):
    urls: list[GetURLsResponseInnerInfo]
    count: int
