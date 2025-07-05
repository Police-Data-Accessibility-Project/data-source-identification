from src.collectors.enums import URLStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters

BATCH_CREATION_PARAMETERS = TestBatchCreationParameters(
    urls=[
        TestURLCreationParameters(
            count=1,
            status=URLStatus.ERROR
        ),
        TestURLCreationParameters(
            count=2,
            status=URLStatus.PENDING
        ),
    ]
)