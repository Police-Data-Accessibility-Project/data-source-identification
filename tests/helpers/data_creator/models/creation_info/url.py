from typing import Optional

from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.db.dtos.url.mapping import URLMapping
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo


class URLCreationInfo(BaseModel):
    url_mappings: list[URLMapping]
    outcome: URLStatus
    annotation_info: Optional[AnnotationInfo] = None

    @property
    def url_ids(self) -> list[int]:
        return [url_mapping.url_id for url_mapping in self.url_mappings]
