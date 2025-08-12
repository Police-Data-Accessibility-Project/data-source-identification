from pendulum import today

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.enums import AgencyAssigned
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.manager.agency import AgencyAssignmentManager
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.core import TestURLSetupEntry
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.data_sources import \
    TestDSURLSetupEntry
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.post import TestURLPostSetupRecord
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.source_collector import \
    TestSCURLSetupEntry


class URLSetupFunctor:

    def __init__(
        self,
        entry: TestURLSetupEntry,
        agency_assignment_manager: AgencyAssignmentManager,
        adb_client: AsyncDatabaseClient
    ):
        self.adb_client = adb_client
        self.agency_assignment_manager = agency_assignment_manager
        self.prime_entry = entry
        self.sc_agency_ids = None
        self.ds_agency_ids = None
        self.sc_url_id = None
        self.ds_response_info = None

    async def __call__(self) -> TestURLPostSetupRecord:
        await self.setup_entry()
        return TestURLPostSetupRecord(
            url_id=self.sc_url_id,
            sc_setup_entry=self.prime_entry.sc_info,
            ds_setup_entry=self.prime_entry.ds_info,
            sc_agency_ids=self.sc_agency_ids,
            ds_agency_ids=self.ds_agency_ids,
            ds_response_info=self.ds_response_info,
            final_url_status=self.prime_entry.final_url_status,
        )

    async def setup_entry(self):
        if self.prime_entry.sc_info is not None:
            self.sc_url_id = await self.setup_sc_entry(self.prime_entry.sc_info)
        if self.prime_entry.ds_info is not None:
            self.ds_response_info = await self.setup_ds_entry(self.prime_entry.ds_info)

    async def get_agency_ids(self, ags: list[AgencyAssigned]):
        results = []
        for ag in ags:
            results.append(await self.agency_assignment_manager.get(ag))
        return results

    async def setup_sc_entry(
        self,
        entry: TestSCURLSetupEntry
    ) -> int:
        """Set up source collector entry and return url id."""
        self.sc_agency_ids = await self.get_agency_ids(self.prime_entry.sc_info.agencies_assigned)
        url = URL(
            url=self.prime_entry.url,
            name=entry.name,
            description=entry.description,
            collector_metadata={},
            status=entry.url_status.value,
            record_type=entry.record_type.value if entry.record_type is not None else None,
            source=URLSource.COLLECTOR
        )
        url_id = await self.adb_client.add(url, return_id=True)
        links = []
        for ag_id in self.sc_agency_ids:
            link = LinkURLAgency(url_id=url_id, agency_id=ag_id)
            links.append(link)
        await self.adb_client.add_all(links)
        return url_id

    async def setup_ds_entry(
        self,
        ds_entry: TestDSURLSetupEntry
    ) -> DataSourcesSyncResponseInnerInfo:
        """Set up data source entry and return response info."""
        self.ds_agency_ids = await self.get_agency_ids(self.prime_entry.ds_info.agencies_assigned)
        return DataSourcesSyncResponseInnerInfo(
            id=ds_entry.id,
            url=self.prime_entry.url,
            name=ds_entry.name,
            description=ds_entry.description,
            url_status=ds_entry.url_status,
            approval_status=ds_entry.approval_status,
            record_type=ds_entry.record_type,
            updated_at=today(),
            agency_ids=self.ds_agency_ids
        )