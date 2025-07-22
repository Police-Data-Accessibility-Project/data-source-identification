import pytest_asyncio

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.collectors.enums import URLStatus
from src.core.enums import SuggestedStatus, RecordType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest_asyncio.fixture
async def batch_url_creation_info(db_data_creator):
    simple_parameter_statuses = [
        URLStatus.VALIDATED,
        URLStatus.SUBMITTED,
        URLStatus.INDIVIDUAL_RECORD,
        URLStatus.NOT_RELEVANT,
        URLStatus.ERROR,
        URLStatus.DUPLICATE,
        URLStatus.NOT_FOUND
    ]
    simple_parameters = [
        TestURLCreationParameters(
            status=status
        ) for status in simple_parameter_statuses
    ]

    parameters = TestBatchCreationParameters(
        urls=[
            *simple_parameters,
            TestURLCreationParameters(
                count=2,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.RELEVANT,
                    user_record_type=RecordType.ARREST_RECORDS,
                    user_agency=URLAgencyAnnotationPostInfo(
                        suggested_agency=await db_data_creator.agency()
                    )
                )
            )
        ]
    )

    return await db_data_creator.batch_v2(parameters=parameters)
