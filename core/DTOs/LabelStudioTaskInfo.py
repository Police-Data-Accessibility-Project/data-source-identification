from pydantic import BaseModel

from collector_db.enums import URLMetadataAttributeType
from core.enums import LabelStudioTaskStatus


class LabelStudioTaskInfo(BaseModel):
    metadata_id: int
    attribute: URLMetadataAttributeType
    task_id: int
    task_status: LabelStudioTaskStatus