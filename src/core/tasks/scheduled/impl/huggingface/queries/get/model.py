from pydantic import BaseModel

from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.huggingface.queries.get.enums import RecordTypeCoarse


class GetForLoadingToHuggingFaceOutput(BaseModel):
    url_id: int
    url: str
    relevant: bool
    record_type_fine: RecordType | None
    record_type_coarse: RecordTypeCoarse | None
    html: str