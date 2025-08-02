from typing import Optional

from pydantic import BaseModel

from src.collectors.enums import CollectorType


class URLHTMLMetadataInfo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class URLMiscellaneousMetadataTDO(BaseModel):
    url_id: int
    collector_metadata: dict
    collector_type: CollectorType
    name: Optional[str] = None
    description: Optional[str] = None
    record_formats: Optional[list[str]] = None
    data_portal_type: Optional[str] = None
    supplying_entity: Optional[str] = None
    html_metadata_info: Optional[URLHTMLMetadataInfo] = None
