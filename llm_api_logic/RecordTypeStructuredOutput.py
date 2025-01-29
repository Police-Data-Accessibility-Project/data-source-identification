"""
Used per the guidance given in Open AI's documentation on structured outputs:
https://platform.openai.com/docs/guides/structured-outputs
"""

from pydantic import BaseModel

from core.enums import RecordType



class RecordTypeStructuredOutput(BaseModel):
    record_type: RecordType