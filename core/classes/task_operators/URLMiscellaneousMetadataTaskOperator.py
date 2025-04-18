from typing import Optional

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLErrorInfos import URLErrorPydanticInfo
from collector_db.enums import TaskType
from collector_manager.enums import CollectorType
from core.DTOs.task_data_objects.URLMiscellaneousMetadataTDO import URLMiscellaneousMetadataTDO
from core.classes.task_operators.TaskOperatorBase import TaskOperatorBase
from core.classes.subtasks.MiscellaneousMetadata.AutoGooglerMiscMetadataSubtask import AutoGooglerMiscMetadataSubtask
from core.classes.subtasks.MiscellaneousMetadata.CKANMiscMetadataSubtask import CKANMiscMetadataSubtask
from core.classes.subtasks.MiscellaneousMetadata.MiscellaneousMetadataSubtaskBase import \
    MiscellaneousMetadataSubtaskBase
from core.classes.subtasks.MiscellaneousMetadata.MuckrockMiscMetadataSubtask import MuckrockMiscMetadataSubtask


class URLMiscellaneousMetadataTaskOperator(TaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient
    ):
        super().__init__(adb_client)

    @property
    def task_type(self):
        return TaskType.MISC_METADATA

    async def meets_task_prerequisites(self):
        return await self.adb_client.has_pending_urls_missing_miscellaneous_metadata()

    async def get_subtask(
            self,
            collector_type: CollectorType
    ) -> Optional[MiscellaneousMetadataSubtaskBase]:
        match collector_type:
            case CollectorType.MUCKROCK_SIMPLE_SEARCH:
                return MuckrockMiscMetadataSubtask()
            case CollectorType.MUCKROCK_COUNTY_SEARCH:
                return MuckrockMiscMetadataSubtask()
            case CollectorType.MUCKROCK_ALL_SEARCH:
                return MuckrockMiscMetadataSubtask()
            case CollectorType.AUTO_GOOGLER:
                return AutoGooglerMiscMetadataSubtask()
            case CollectorType.CKAN:
                return CKANMiscMetadataSubtask()
            case _:
                return None

    async def html_default_logic(self, tdo: URLMiscellaneousMetadataTDO):
        if tdo.name is None:
            tdo.name = tdo.html_metadata_info.title
        if tdo.description is None:
            tdo.description = tdo.html_metadata_info.description

    async def inner_task_logic(self):
        tdos: list[URLMiscellaneousMetadataTDO] = await self.adb_client.get_pending_urls_missing_miscellaneous_metadata()
        await self.link_urls_to_task(url_ids=[tdo.url_id for tdo in tdos])

        error_infos = []
        for tdo in tdos:
            subtask = await self.get_subtask(tdo.collector_type)
            try:
                if subtask is not None:
                    subtask.process(tdo)
                await self.html_default_logic(tdo)
            except Exception as e:
                error_info = URLErrorPydanticInfo(
                    task_id=self.task_id,
                    url_id=tdo.url_id,
                    error=str(e),
                )
                error_infos.append(error_info)

        await self.adb_client.add_miscellaneous_metadata(tdos)
        await self.adb_client.add_url_error_infos(error_infos)