import datetime
from typing import Optional

from pydantic import BaseModel, model_validator

from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


class TestBatchCreationParameters(BaseModel):
    created_at: Optional[datetime.datetime] = None
    outcome: BatchStatus = BatchStatus.READY_TO_LABEL
    strategy: CollectorType = CollectorType.EXAMPLE
    urls: Optional[list[TestURLCreationParameters]] = None

    @model_validator(mode='after')
    def validate_urls(self):
        if self.outcome != BatchStatus.READY_TO_LABEL:
            if self.urls is not None:
                raise ValueError('URLs cannot be provided if outcome is not READY_TO_LABEL')
            return self

        if self.urls is None:
            self.urls = [TestURLCreationParameters(count=1)]
        return self
