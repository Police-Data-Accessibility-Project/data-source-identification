from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch

from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.confirmed_url_agency import ConfirmedURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source import URLDataSource
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo, DataSourcesSyncResponseInnerInfo
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.data import TestURLSetupEntry, \
    SyncResponseOrder, TestURLPostSetupRecord, AgencyAssigned
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.info import TestDataSourcesSyncSetupInfo
from tests.helpers.db_data_creator import DBDataCreator


async def setup_data(
    db_data_creator: DBDataCreator,
    mock_pdap_client: PDAPClient
) -> TestDataSourcesSyncSetupInfo:
    adb_client = db_data_creator.adb_client

    agency_id_preexisting_urls = await db_data_creator.agency()
    agency_id_new_urls = await db_data_creator.agency()

    # Setup data sources


    # Setup pre-existing urls
    preexisting_urls = [
        URL(
            url='https://example.com/1',
            name='Pre-existing URL 1',
            description='Pre-existing URL 1 Description',
            collector_metadata={},
            outcome=URLStatus.PENDING.value,
            record_type=RecordType.ACCIDENT_REPORTS.value,
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ),
        URL(
            url='https://example.com/2',
            name='Pre-existing URL 2',
            description='Pre-existing URL 2 Description',
            collector_metadata={},
            outcome=URLStatus.VALIDATED.value,
            record_type=RecordType.ACCIDENT_REPORTS.value,
            updated_at=datetime(2025, 10, 17, 3, 0, 0),
        ),
    ]
    preexisting_url_ids = await adb_client.add_all(preexisting_urls, return_ids=True)
    # Link second pre-existing url to data source
    await adb_client.add(URLDataSource(
        url_id=preexisting_url_ids[1],
        data_source_id=preexisting_url_ids[1]
    ))

    # Link second pre-existing url to agency
    await adb_client.add(ConfirmedURLAgency(
        url_id=preexisting_url_ids[1],
        agency_id=agency_id_preexisting_urls
    ))


    first_call_response = DataSourcesSyncResponseInfo(
        data_sources=[
            DataSourcesSyncResponseInnerInfo(
                id=120,
                url="https://newurl.com/1",
                name="New URL 1",
                description="New URL 1 Description",
                approval_status=ApprovalStatus.APPROVED,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.ACCIDENT_REPORTS,
                agency_ids=[agency_id_new_urls],
                url_status=DataSourcesURLStatus.OK
            ),
            DataSourcesSyncResponseInnerInfo(
                id=121,
                url="https://newurl.com/2",
                name="New URL 2",
                description="New URL 2 Description",
                approval_status=ApprovalStatus.APPROVED,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.FIELD_CONTACTS,
                agency_ids=[agency_id_new_urls],
                url_status=DataSourcesURLStatus.BROKEN
            ),
            DataSourcesSyncResponseInnerInfo(
                id=122,
                url="https://newurl.com/3",
                name="New URL 3",
                description="New URL 3 Description",
                approval_status=ApprovalStatus.PENDING,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.WANTED_PERSONS,
                agency_ids=[agency_id_new_urls],
                url_status=DataSourcesURLStatus.OK
            ),
            DataSourcesSyncResponseInnerInfo(
                id=123,
                url="https://newurl.com/4",
                name="New URL 4",
                description="New URL 4 Description",
                approval_status=ApprovalStatus.NEEDS_IDENTIFICATION,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.STOPS,
                agency_ids=[agency_id_new_urls],
                url_status=DataSourcesURLStatus.OK
            ),
            DataSourcesSyncResponseInnerInfo(
                id=preexisting_url_ids[0],
                url="https://newurl.com/5",
                name="Updated Preexisting URL 1",
                description="Updated Preexisting URL 1 Description",
                approval_status=ApprovalStatus.REJECTED,  # Status should update to rejected.
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.BOOKING_REPORTS,
                agency_ids=[agency_id_preexisting_urls, agency_id_new_urls],
                url_status=DataSourcesURLStatus.OK
            )
        ]
    )
    second_call_response = DataSourcesSyncResponseInfo(
        data_sources=[
            DataSourcesSyncResponseInnerInfo(
                id=preexisting_url_ids[1],
                url="https://newurl.com/6",
                name="Updated Preexisting URL 2",
                description="Updated Preexisting URL 2 Description",
                approval_status=ApprovalStatus.APPROVED,  # SC should stay validated
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.PERSONNEL_RECORDS,
                agency_ids=[agency_id_new_urls],
                url_status=DataSourcesURLStatus.OK
            ),
        ]
    )
    third_call_response = DataSourcesSyncResponseInfo(data_sources=[])




class DataSourcesSyncTestSetupManager:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        entries: list[TestURLSetupEntry]
    ):
        self.adb_client = adb_client
        self.entries = entries

        self.response_dict: dict[
            SyncResponseOrder, list[DataSourcesSyncResponseInfo]
        ] = {
            e: [] for e in SyncResponseOrder
        }
        self.test_agency_dict: dict[
            AgencyAssigned, int
        ] = {}

    async def setup(self):
        await self.setup_agencies()

    async def setup_entries(self):
        for entry in self.entries:
            await self.setup_entry(entry)

    async def setup_entry(
        self,
        entry: TestURLSetupEntry
    ) -> TestURLPostSetupRecord:
        if entry.sc_info is not None:
            # TODO: Add SC entry
            raise NotImplementedError()
        if entry.ds_info is not None:
            # TODO: Add DS entry
            raise NotImplementedError()


@contextmanager
def patch_sync_data_sources(side_effects: list):
    with patch.object(
        PDAPClient,
        "sync_data_sources",
        side_effect=side_effects
    ):
        yield