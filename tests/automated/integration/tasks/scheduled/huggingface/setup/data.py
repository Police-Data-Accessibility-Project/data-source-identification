from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.entry import TestURLSetupEntry
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters

ENTRIES = [
        # Because pending, should not be picked up
        TestURLSetupEntry(
            creation_parameters=TestURLCreationParameters(
                status=URLStatus.PENDING,
                with_html_content=True
            ),
            picked_up=False
        ),
        # Because no html content, should not be picked up
        TestURLSetupEntry(
            creation_parameters=TestURLCreationParameters(
                status=URLStatus.SUBMITTED,
                with_html_content=False
            ),
            picked_up=False
        ),
        # Remainder should be picked up
        TestURLSetupEntry(
            creation_parameters=TestURLCreationParameters(
                status=URLStatus.SUBMITTED,
                with_html_content=True
            ),
            picked_up=True
        ),
        TestURLSetupEntry(
            creation_parameters=TestURLCreationParameters(
                status=URLStatus.VALIDATED,
                with_html_content=True
            ),
            picked_up=True
        ),
        TestURLSetupEntry(
            creation_parameters=TestURLCreationParameters(
                status=URLStatus.NOT_RELEVANT,
                with_html_content=True
            ),
            picked_up=True
        ),
]
