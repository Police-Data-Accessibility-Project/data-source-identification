from aiohttp import ClientSession

from agency_identifier.MuckrockAPIInterface import MuckrockAPIInterface
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.enums import TaskType
from collector_manager.enums import CollectorType
from core.DTOs.URLAgencySuggestionInfo import URLAgencySuggestionInfo
from core.DTOs.task_data_objects.AgencyIdentificationTDO import AgencyIdentificationTDO
from core.classes.task_operators.TaskOperatorBase import TaskOperatorBase
from core.classes.subtasks.AutoGooglerAgencyIdentificationSubtask import AutoGooglerAgencyIdentificationSubtask
from core.classes.subtasks.CKANAgencyIdentificationSubtask import CKANAgencyIdentificationSubtask
from core.classes.subtasks.CommonCrawlerAgencyIdentificationSubtask import CommonCrawlerAgencyIdentificationSubtask
from core.classes.subtasks.MuckrockAgencyIdentificationSubtask import MuckrockAgencyIdentificationSubtask
from core.enums import SuggestionType
from pdap_api_client.PDAPClient import PDAPClient


# TODO: Validate with Manual Tests

class AgencyIdentificationTaskOperator(TaskOperatorBase):

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
    def task_type(self):
        return TaskType.AGENCY_IDENTIFICATION

    async def meets_task_prerequisites(self):
        has_urls_without_agency_suggestions = await self.adb_client.has_urls_without_agency_suggestions()
        return has_urls_without_agency_suggestions

    async def get_pending_urls_without_agency_identification(self):
        return await self.adb_client.get_urls_without_agency_suggestions()

    async def get_muckrock_subtask(self):
        return MuckrockAgencyIdentificationSubtask(
            muckrock_api_interface=self.muckrock_api_interface,
            pdap_client=self.pdap_client
        )

    async def get_subtask(self, collector_type: CollectorType):
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

    @staticmethod
    async def run_subtask(subtask, url_id, collector_metadata) -> list[URLAgencySuggestionInfo]:
        return await subtask.run(url_id=url_id, collector_metadata=collector_metadata)

    async def inner_task_logic(self):
        async with ClientSession() as session:
            self.pdap_client.access_manager.session = session
            self.muckrock_api_interface.session = session
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


