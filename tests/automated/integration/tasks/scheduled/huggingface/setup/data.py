from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.core.tasks.scheduled.huggingface.queries.get.enums import RecordTypeCoarse
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.entry \
    import TestPushToHuggingFaceURLSetupEntry as Entry
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.output import \
    TestPushToHuggingFaceURLSetupExpectedOutput as Output
from tests.automated.integration.tasks.scheduled.huggingface.setup.models.input import \
    TestPushToHuggingFaceURLSetupEntryInput as Input

ENTRIES = [
        # Because pending, should not be picked up
        Entry(
            input=Input(
                outcome=URLStatus.PENDING,
                has_html_content=True,
                record_type=RecordType.INCARCERATION_RECORDS
            ),
            expected_output=Output(
                picked_up=False,
            )
        ),
        # Because no html content, should not be picked up
        Entry(
            input=Input(
                outcome=URLStatus.SUBMITTED,
                has_html_content=False,
                record_type=RecordType.RECORDS_REQUEST_INFO
            ),
            expected_output=Output(
                picked_up=False,
            )
        ),
        # Remainder should be picked up
        Entry(
            input=Input(
                outcome=URLStatus.VALIDATED,
                has_html_content=True,
                record_type=RecordType.RECORDS_REQUEST_INFO
            ),
            expected_output=Output(
                picked_up=True,
                coarse_record_type=RecordTypeCoarse.AGENCY_PUBLISHED_RESOURCES,
                relevant=True
            )
        ),
        Entry(
            input=Input(
                outcome=URLStatus.SUBMITTED,
                has_html_content=True,
                record_type=RecordType.INCARCERATION_RECORDS
            ),
            expected_output=Output(
                picked_up=True,
                coarse_record_type=RecordTypeCoarse.JAILS_AND_COURTS,
                relevant=True
            )
        ),
        Entry(
            input=Input(
                outcome=URLStatus.NOT_RELEVANT,
                has_html_content=True,
                record_type=None
            ),
            expected_output=Output(
                picked_up=True,
                coarse_record_type=RecordTypeCoarse.NOT_RELEVANT,
                relevant=False
            )
        ),
]
