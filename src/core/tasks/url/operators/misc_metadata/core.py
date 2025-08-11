from typing import Optional

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.enums import TaskType
from src.collectors.enums import CollectorType
from src.core.tasks.url.operators.misc_metadata.tdo import URLMiscellaneousMetadataTDO
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.subtasks.miscellaneous_metadata.auto_googler import AutoGooglerMiscMetadataSubtask
from src.core.tasks.url.subtasks.miscellaneous_metadata.ckan import CKANMiscMetadataSubtask
from src.core.tasks.url.subtasks.miscellaneous_metadata.base import \
    MiscellaneousMetadataSubtaskBase
from src.core.tasks.url.subtasks.miscellaneous_metadata.muckrock import MuckrockMiscMetadataSubtask


class URLMiscellaneousMetadataTaskOperator(URLTaskOperatorBase):

    def __init__(
            self,
            adb_client: AsyncDatabaseClient
    ):
        super().__init__(adb_client)

    @property
    def task_type(self) -> TaskType:
        return TaskType.MISC_METADATA

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.has_pending_urls_missing_miscellaneous_metadata()

    async def get_subtask(
            self,
            collector_type: CollectorType
    ) -> MiscellaneousMetadataSubtaskBase | None:
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
        """
        Modifies:
            tdo.name
            tdo.description
        """
        if tdo.name is None:
            tdo.name = tdo.html_metadata_info.title
        if tdo.description is None:
            tdo.description = tdo.html_metadata_info.description

    async def inner_task_logic(self) -> None:
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