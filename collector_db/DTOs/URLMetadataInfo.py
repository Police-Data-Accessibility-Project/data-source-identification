from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from collector_db.models import URLAttributeType, ValidationStatus, ValidationSource


class URLMetadataInfo(BaseModel):
    url_id: int
    attribute: URLAttributeType
    # TODO: May need to add validation here depending on the type of attribute
    value: str
    validation_status: ValidationStatus
    validation_source: ValidationSource
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None