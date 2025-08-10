from unittest.mock import AsyncMock

from src.core.tasks.url.operators.auto_relevant.core import URLAutoRelevantTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.inference.models.output import BasicOutput
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator


async def setup_operator(adb_client: AsyncDatabaseClient) -> URLAutoRelevantTaskOperator:
    """Create pending urls with compressed html data and no auto relevant suggestion"""
    mock_hf_client = AsyncMock()
    mock_hf_client.get_relevancy_annotation.side_effect = [
        BasicOutput(
            annotation=True,
            confidence=0.5,
            model="test_model"
        ),
        BasicOutput(
            annotation=False,
            confidence=0.5,
            model="test_model"
        ),
        Exception("test exception")
    ]
    return URLAutoRelevantTaskOperator(
        adb_client=adb_client,
        hf_client=mock_hf_client
    )

async def setup_urls(db_data_creator: DBDataCreator) -> list[int]:
    """Create pending urls with compressed html data and no auto relevant suggestion"""
    parameters = TestBatchCreationParameters(
        urls=[
            TestURLCreationParameters(
                count=3,
                with_html_content=True
            )
        ]
    )

    batch_url_creation_info = await db_data_creator.batch_v2(parameters=parameters)

    return batch_url_creation_info.url_ids