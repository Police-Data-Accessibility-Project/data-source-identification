from collections import defaultdict

from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo, DataSourcesSyncResponseInfo
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.enums import SyncResponseOrder
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.manager.agency import AgencyAssignmentManager
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.manager.queries.check import \
    CheckURLQueryBuilder
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.manager.url import URLSetupFunctor
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.core import TestURLSetupEntry
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.models.url.post import TestURLPostSetupRecord


class DataSourcesSyncTestSetupManager:

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        entries: list[TestURLSetupEntry],
    ):
        self.adb_client = adb_client
        self.entries = entries
        self.agency_assignment_manager = AgencyAssignmentManager(self.adb_client)

        self.url_id_to_setup_record: dict[int, TestURLPostSetupRecord] = {}
        self.ds_id_to_setup_record: dict[int, TestURLPostSetupRecord] = {}
        self.sync_response_order_to_setup_record: dict[
            SyncResponseOrder, list[TestURLPostSetupRecord]
        ] = defaultdict(list)

        self.response_dict: dict[
            SyncResponseOrder, list[DataSourcesSyncResponseInnerInfo]
        ] = defaultdict(list)

    async def setup(self):
        await self.setup_agencies()
        await self.setup_entries()

    async def setup_entries(self):
        for entry in self.entries:
            await self.setup_entry(entry)

    async def setup_entry(
        self,
        entry: TestURLSetupEntry
    ) -> None:
        """
        Modifies:
            self.url_id_to_setup_record
            self.ds_id_to_setup_record
            self.response_dict
        """
        functor = URLSetupFunctor(
            entry=entry,
            agency_assignment_manager=self.agency_assignment_manager,
            adb_client=self.adb_client
        )
        result = await functor()
        response_info = result.ds_response_info
        if response_info is not None:
            self.response_dict[entry.ds_info.sync_response_order].append(response_info)
        if result.url_id is not None:
            self.url_id_to_setup_record[result.url_id] = result
        if result.data_sources_id is not None:
            self.ds_id_to_setup_record[result.data_sources_id] = result
        if entry.ds_info is not None:
            self.sync_response_order_to_setup_record[
                entry.ds_info.sync_response_order
            ].append(result)

    async def setup_agencies(self):
        await self.agency_assignment_manager.setup()

    async def get_data_sources_sync_responses(
        self,
        orders: list[SyncResponseOrder | ValueError]
    ) -> list[DataSourcesSyncResponseInfo]:
        results = []
        for order in orders:
            results.append(
                DataSourcesSyncResponseInfo(
                    data_sources=self.response_dict[order]
                )
            )
        return results

    async def check_via_url(self, url_id: int):
        builder = CheckURLQueryBuilder(
            record=self.url_id_to_setup_record[url_id]
        )
        await self.adb_client.run_query_builder(builder)

    async def check_via_data_source(self, data_source_id: int):
        builder = CheckURLQueryBuilder(
            record=self.ds_id_to_setup_record[data_source_id]
        )
        await self.adb_client.run_query_builder(builder)

    async def check_results(self):
        for url_id in self.url_id_to_setup_record.keys():
            await self.check_via_url(url_id)
        for data_source_id in self.ds_id_to_setup_record.keys():
            await self.check_via_data_source(data_source_id)

    async def check_via_sync_response_order(self, order: SyncResponseOrder):
        records = self.sync_response_order_to_setup_record[order]
        for record in records:
            builder = CheckURLQueryBuilder(
                record=record
            )
            await self.adb_client.run_query_builder(builder)
