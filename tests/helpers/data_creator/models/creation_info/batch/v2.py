from pydantic import BaseModel

from src.collectors.enums import URLStatus
from tests.helpers.data_creator.models.creation_info.url import URLCreationInfo

class BatchURLCreationInfoV2(BaseModel):
    batch_id: int
    urls_by_status: dict[URLStatus, URLCreationInfo] = {}
    urls_by_order: list[URLCreationInfo] = []  # URLs in order of inclusion in parameters

    @property
    def url_ids(self) -> list[int]:
        url_creation_infos = self.urls_by_status.values()
        url_ids = []
        for url_creation_info in url_creation_infos:
            url_ids.extend(url_creation_info.url_ids)
        return url_ids
