from enum import Enum

from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.external.pdap.enums import DataSourcesURLStatus, ApprovalStatus

class SyncResponseOrder(Enum):
    """Represents which sync response the entry is in."""
    FIRST = 1
    SECOND = 2
    # No entries should be in 3
    THIRD = 3

class AgencyAssigned(Enum):
    """Represents which of several pre-created agencies the entry is assigned to."""
    ONE = 1
    TWO = 2
    THREE = 3

class TestDSURLSetupEntry(BaseModel):
    """Represents URL previously existing in DS DB.

    These values should overwrite any SC values
    """
    id: int  # ID of URL in DS App
    name: str
    description: str
    url_status: DataSourcesURLStatus
    approval_status: ApprovalStatus
    record_type: RecordType
    agency_ids: list[AgencyAssigned]
    sync_response_order: SyncResponseOrder

class TestSCURLSetupEntry(BaseModel):
    """Represents URL previously existing in SC DB.

    These values should be overridden by any DS values
    """
    name: str
    description: str
    record_type: RecordType
    url_status: URLStatus
    agency_ids: list[AgencyAssigned]

class TestURLSetupEntry(BaseModel):
    url: str
    ds_info: TestDSURLSetupEntry | None # Represents URL previously existing in DS DB
    sc_info: TestSCURLSetupEntry | None # Represents URL previously existing in SC DB

    final_status: URLStatus

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
            agency_ids=[AgencyAssigned.ONE, AgencyAssigned.TWO],
            sync_response_order=SyncResponseOrder.FIRST
        ),
        sc_info=TestSCURLSetupEntry(
            name='Pre-existing URL 1',
            description='Pre-existing URL 1 Description',
            record_type=RecordType.ACCIDENT_REPORTS,
            url_status=URLStatus.PENDING,
            agency_ids=[AgencyAssigned.ONE, AgencyAssigned.THREE]
        ),
        final_status=URLStatus.VALIDATED
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
            agency_ids=[AgencyAssigned.TWO],
            sync_response_order=SyncResponseOrder.FIRST
        ),
        sc_info=None,
        final_status=URLStatus.NOT_FOUND
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
            agency_ids=[AgencyAssigned.ONE, AgencyAssigned.THREE]
        ),
        final_status=URLStatus.PENDING
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
            agency_ids=[AgencyAssigned.ONE],
            sync_response_order=SyncResponseOrder.FIRST
        ),
        sc_info=None,
        final_status=URLStatus.NOT_RELEVANT
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
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_ids=[AgencyAssigned.ONE],
            sync_response_order=SyncResponseOrder.SECOND
        ),
        sc_info=TestSCURLSetupEntry(
            name='Pre-existing URL 5 Name',
            description='Pre-existing URL 5 Description',
            record_type=RecordType.ACCIDENT_REPORTS,
            url_status=URLStatus.PENDING,
            agency_ids=[]
        ),
        final_status=URLStatus.VALIDATED

    )
]

class TestURLPostSetupRecord(BaseModel):
    """Stores a setup entry along with relevant database-generated ids"""
    url_id: int
    sc_setup_entry: TestSCURLSetupEntry | None
    ds_setup_entry: TestDSURLSetupEntry | None
    sc_agency_ids: list[int] | None
    ds_agency_ids: list[int] | None