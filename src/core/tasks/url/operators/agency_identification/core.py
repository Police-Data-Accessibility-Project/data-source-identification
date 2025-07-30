from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.dtos.tdo import AgencyIdentificationTDO
from src.core.tasks.url.operators.agency_identification.subtasks.base import AgencyIdentificationSubtaskBase
from src.core.tasks.url.operators.agency_identification.subtasks.no_collector import \
    NoCollectorAgencyIdentificationSubtask
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.collectors.enums import CollectorType
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.agency_identification.subtasks.auto_googler import AutoGooglerAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.ckan import CKANAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.common_crawler import CommonCrawlerAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.muckrock import MuckrockAgencyIdentificationSubtask
from src.core.enums import SuggestionType
from src.external.pdap.client import PDAPClient


class AgencyIdentificationTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            pdap_client: PDAPClient,
            muckrock_api_interface: MuckrockAPIInterface,
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client
        self.muckrock_api_interface = muckrock_api_interface

    @property
    def task_type(self) -> TaskType:
        return TaskType.AGENCY_IDENTIFICATION

    async def meets_task_prerequisites(self) -> bool:
        has_urls_without_agency_suggestions = await self.adb_client.has_urls_without_agency_suggestions()
        return has_urls_without_agency_suggestions

    async def get_pending_urls_without_agency_identification(self) -> list[AgencyIdentificationTDO]:
        return await self.adb_client.get_urls_without_agency_suggestions()

    async def get_muckrock_subtask(self) -> MuckrockAgencyIdentificationSubtask:
        return MuckrockAgencyIdentificationSubtask(
            muckrock_api_interface=self.muckrock_api_interface,
            pdap_client=self.pdap_client
        )

    async def get_subtask(
        self,
        collector_type: CollectorType
    ) -> AgencyIdentificationSubtaskBase:
        match collector_type:
            case CollectorType.MUCKROCK_SIMPLE_SEARCH:
                return await self.get_muckrock_subtask()
            case CollectorType.MUCKROCK_COUNTY_SEARCH:
                return await self.get_muckrock_subtask()
            case CollectorType.MUCKROCK_ALL_SEARCH:
                return await self.get_muckrock_subtask()
            case CollectorType.AUTO_GOOGLER:
                return AutoGooglerAgencyIdentificationSubtask()
            case CollectorType.COMMON_CRAWLER:
                return CommonCrawlerAgencyIdentificationSubtask()
            case CollectorType.CKAN:
                return CKANAgencyIdentificationSubtask(
                    pdap_client=self.pdap_client
                )
        return NoCollectorAgencyIdentificationSubtask()

    @staticmethod
    async def run_subtask(subtask, url_id, collector_metadata) -> list[URLAgencySuggestionInfo]:
        return await subtask.run(url_id=url_id, collector_metadata=collector_metadata)

    async def inner_task_logic(self) -> None:
        tdos: list[AgencyIdentificationTDO] = await self.get_pending_urls_without_agency_identification()
        await self.link_urls_to_task(url_ids=[tdo.url_id for tdo in tdos])
        error_infos = []
        all_agency_suggestions = []
        for tdo in tdos:
            subtask = await self.get_subtask(tdo.collector_type)
            try:
                new_agency_suggestions = await self.run_subtask(
                    subtask,
                    tdo.url_id,
                    tdo.collector_metadata
                )
                all_agency_suggestions.extend(new_agency_suggestions)
            except Exception as e:
                error_info = URLErrorPydanticInfo(
                    task_id=self.task_id,
                    url_id=tdo.url_id,
                    error=str(e),
                )
                error_infos.append(error_info)

        non_unknown_agency_suggestions = [suggestion for suggestion in all_agency_suggestions if suggestion.suggestion_type != SuggestionType.UNKNOWN]
        await self.adb_client.upsert_new_agencies(non_unknown_agency_suggestions)
        confirmed_suggestions = [suggestion for suggestion in all_agency_suggestions if suggestion.suggestion_type == SuggestionType.CONFIRMED]
        await self.adb_client.add_confirmed_agency_url_links(confirmed_suggestions)
        non_confirmed_suggestions = [suggestion for suggestion in all_agency_suggestions if suggestion.suggestion_type != SuggestionType.CONFIRMED]
        await self.adb_client.add_agency_auto_suggestions(non_confirmed_suggestions)
        await self.adb_client.add_url_error_infos(error_infos)


