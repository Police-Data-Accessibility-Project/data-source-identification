from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.external.pdap.enums import DataSourcesURLStatus, ApprovalStatus
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.models.url.data_sources import TestDSURLSetupEntry
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.enums import SyncResponseOrder, AgencyAssigned
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.models.url.source_collector import TestSCURLSetupEntry
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.models.url.core import TestURLSetupEntry

ENTRIES = [
    TestURLSetupEntry(
        # A URL in both DBs that should be overwritten
        url='https://example.com/1',
        ds_info=TestDSURLSetupEntry(
            id=100,
            name='Overwritten URL 1 Name',
            description='Overwritten URL 1 Description',
            url_status=DataSourcesURLStatus.OK,
            approval_status=ApprovalStatus.APPROVED,
            record_type=RecordType.ACCIDENT_REPORTS,
            agencies_assigned=[AgencyAssigned.ONE, AgencyAssigned.TWO],
            sync_response_order=SyncResponseOrder.FIRST
        ),
        sc_info=TestSCURLSetupEntry(
            name='Pre-existing URL 1',
            description='Pre-existing URL 1 Description',
            record_type=RecordType.ACCIDENT_REPORTS,
            url_status=URLStatus.PENDING,
            agencies_assigned=[AgencyAssigned.ONE, AgencyAssigned.THREE]
        ),
        final_url_status=URLStatus.VALIDATED
    ),
    TestURLSetupEntry(
        # A DS-only approved but broken URL
        url='https://example.com/2',
        ds_info=TestDSURLSetupEntry(
            id=101,
            name='New URL 2 Name',
            description='New URL 2 Description',
            url_status=DataSourcesURLStatus.BROKEN,
            approval_status=ApprovalStatus.APPROVED,
            record_type=RecordType.INCARCERATION_RECORDS,
            agencies_assigned=[AgencyAssigned.TWO],
            sync_response_order=SyncResponseOrder.FIRST
        ),
        sc_info=None,
        final_url_status=URLStatus.NOT_FOUND
    ),
    TestURLSetupEntry(
        # An SC-only pending URL, should be unchanged.
        url='https://example.com/3',
        ds_info=None,
        sc_info=TestSCURLSetupEntry(
            name='Pre-existing URL 3 Name',
            description='Pre-existing URL 3 Description',
            record_type=RecordType.FIELD_CONTACTS,
            url_status=URLStatus.PENDING,
            agencies_assigned=[AgencyAssigned.ONE, AgencyAssigned.THREE]
        ),
        final_url_status=URLStatus.PENDING
    ),
    TestURLSetupEntry(
        # A DS-only rejected URL
        url='https://example.com/4',
        ds_info=TestDSURLSetupEntry(
            id=102,
            name='New URL 4 Name',
            description='New URL 4 Description',
            url_status=DataSourcesURLStatus.OK,
            approval_status=ApprovalStatus.REJECTED,
            record_type=RecordType.ACCIDENT_REPORTS,
            agencies_assigned=[AgencyAssigned.ONE],
            sync_response_order=SyncResponseOrder.FIRST
        ),
        sc_info=None,
        final_url_status=URLStatus.NOT_RELEVANT
    ),
    TestURLSetupEntry(
        # A pre-existing URL in the second response
        url='https://example.com/5',
        ds_info=TestDSURLSetupEntry(
            id=103,
            name='New URL 5 Name',
            description='New URL 5 Description',
            url_status=DataSourcesURLStatus.OK,
            approval_status=ApprovalStatus.APPROVED,
            record_type=RecordType.INCARCERATION_RECORDS,
            agencies_assigned=[AgencyAssigned.ONE],
            sync_response_order=SyncResponseOrder.SECOND
        ),
        sc_info=TestSCURLSetupEntry(
            name='Pre-existing URL 5 Name',
            description='Pre-existing URL 5 Description',
            record_type=None,
            url_status=URLStatus.PENDING,
            agencies_assigned=[]
        ),
        final_url_status=URLStatus.VALIDATED

    )
]

