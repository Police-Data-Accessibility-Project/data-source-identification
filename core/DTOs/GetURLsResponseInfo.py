import datetime
from typing import Optional

from pydantic import BaseModel

from collector_db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource
from collector_manager.enums import URLStatus

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
    batch_id: int
    url: str
    status: URLStatus
    collector_metadata: Optional[dict]
    updated_at: datetime.datetime
    created_at: datetime.datetime
    errors: list[GetURLsResponseErrorInfo]
    metadata: list[GetURLsResponseMetadataInfo]

class GetURLsResponseInfo(BaseModel):
    urls: list[GetURLsResponseInnerInfo]
    count: int
