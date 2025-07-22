from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.instantiations.confirmed_url_agency import ConfirmedURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.data_source import URLDataSource
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo, DataSourcesSyncResponseInnerInfo
from src.external.pdap.enums import ApprovalStatus
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
                record_type=RecordType.ACCIDENT_REPORTS.value,
                agency_ids=[agency_id_new_urls],
            ),
            DataSourcesSyncResponseInnerInfo(
                id=121,
                url="https://newurl.com/2",
                name="New URL 2",
                description="New URL 2 Description",
                approval_status=ApprovalStatus.APPROVED,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.ACCIDENT_REPORTS.value,
                agency_ids=[agency_id_new_urls],
            ),
            DataSourcesSyncResponseInnerInfo(
                id=122,
                url="https://newurl.com/3",
                name="New URL 3",
                description="New URL 3 Description",
                approval_status=ApprovalStatus.APPROVED,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.ACCIDENT_REPORTS.value,
                agency_ids=[agency_id_new_urls],
            ),
            DataSourcesSyncResponseInnerInfo(
                id=123,
                url="https://newurl.com/4",
                name="New URL 4",
                description="New URL 4 Description",
                approval_status=ApprovalStatus.APPROVED,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.ACCIDENT_REPORTS.value,
                agency_ids=[agency_id_new_urls],
            ),
            DataSourcesSyncResponseInnerInfo(
                id=preexisting_url_ids[0],
                url="https://newurl.com/5",
                name="Updated Preexisting URL 1",
                description="Updated Preexisting URL 1 Description",
                approval_status=ApprovalStatus.APPROVED,
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
                record_type=RecordType.ACCIDENT_REPORTS.value,
                agency_ids=[agency_id_preexisting_urls, agency_id_new_urls],
        ]

    )






@contextmanager
def patch_sync_data_sources(side_effects: list):
    with patch.object(
        PDAPClient,
        "sync_data_sources",
        side_effect=side_effects
    ):
        yield