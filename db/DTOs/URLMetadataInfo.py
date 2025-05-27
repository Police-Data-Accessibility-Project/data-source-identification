from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource


class URLMetadataInfo(BaseModel):
    id: Optional[int] = None
    url_id: Optional[int] = None
    attribute: Optional[URLMetadataAttributeType] = None
    # TODO: May need to add validation here depending on the type of attribute
    value: Optional[str] = None
    notes: Optional[str] = None
    validation_status: Optional[ValidationStatus] = None
    validation_source: Optional[ValidationSource] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None