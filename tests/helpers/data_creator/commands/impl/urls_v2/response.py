from pydantic import BaseModel

from src.collectors.enums import URLStatus
from tests.helpers.data_creator.models.creation_info.url import URLCreationInfo


class URLsV2Response(BaseModel):
    urls_by_status: dict[URLStatus, URLCreationInfo] = {}
    urls_by_order: list[URLCreationInfo] = []