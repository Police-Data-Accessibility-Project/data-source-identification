from pydantic import BaseModel

from core.enums import RecordType


class RecordTypeAnnotationPostInfo(BaseModel):
    record_type: RecordType