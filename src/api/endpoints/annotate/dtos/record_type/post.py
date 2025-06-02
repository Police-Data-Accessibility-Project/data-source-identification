from pydantic import BaseModel

from src.core.enums import RecordType


class RecordTypeAnnotationPostInfo(BaseModel):
    record_type: RecordType