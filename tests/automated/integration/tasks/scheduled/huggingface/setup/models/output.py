from typing import Self

from pydantic import BaseModel, model_validator

from src.core.enums import RecordType
from src.core.tasks.scheduled.huggingface.queries.get.enums import RecordTypeCoarse


class TestPushToHuggingFaceURLSetupExpectedOutput(BaseModel):
    picked_up: bool
    relevant: bool | None = None
    coarse_record_type: RecordTypeCoarse | None = None

    @model_validator(mode='after')
    def validate_coarse_record_type_and_relevant(self) -> Self:
        if not self.picked_up:
            return self
        if self.coarse_record_type is None:
            raise ValueError('Coarse record type should be provided if picked up')
        if self.relevant is None:
            raise ValueError('Relevant should be provided if picked up')
        return self
