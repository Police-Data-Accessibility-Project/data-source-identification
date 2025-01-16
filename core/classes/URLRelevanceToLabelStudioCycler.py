from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.RelevanceLabelStudioInputCycleInfo import RelevanceLabelStudioInputCycleInfo
from collector_db.enums import URLMetadataAttributeType, ValidationStatus
from core.DTOs.LabelStudioTaskInfo import LabelStudioTaskInfo
from core.DTOs.URLRelevanceHuggingfaceCycleInfo import URLRelevanceHuggingfaceCycleInfo
from core.enums import LabelStudioTaskStatus
from label_studio_interface.DTOs.LabelStudioTaskExportInfo import LabelStudioTaskExportInfo, \
    add_html_info_to_export_info
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager


class URLRelevanceToLabelStudioCycler:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            label_studio_api_manager: LabelStudioAPIManager
    ):
        self.adb_client = adb_client
        self.label_studio_api_manager = label_studio_api_manager

    async def cycle(self):
        # Get max 100 Pending URLs from Source Collector
        # with URL Metadata Relevant
        # Attribute validation status Pending Label Studio
        cycle_infos = await self.get_cycle_infos()
        # Pipe into label studio
        metadata_ids = [cycle_info.metadata_id for cycle_info in cycle_infos]
        await self.pipe_into_label_studio_and_update_db(cycle_infos)

        # Update relevant URLMetadata entry with validation status In Label Studio
        await self.update_relevant_metadata(metadata_ids)

    async def update_relevant_metadata(self, metadata_ids):
        await self.adb_client.update_url_metadata_status(
            metadata_ids=metadata_ids,
            validation_status=ValidationStatus.IN_LABEL_STUDIO
        )

    async def construct_export_infos(
            self,
            cycle_infos: list[RelevanceLabelStudioInputCycleInfo]
    ) -> list[LabelStudioTaskExportInfo]:
        export_infos = []
        for cycle_info in cycle_infos:
            export_info = LabelStudioTaskExportInfo(url=cycle_info.url)
            for html_content_info in cycle_info.html_content_info:
                add_html_info_to_export_info(
                    export_info=export_info,
                    html_content_info=html_content_info
                )
            export_infos.append(export_info)
        return export_infos

    async def pipe_into_label_studio_and_update_db(self, cycle_infos):
        export_infos = await self.construct_export_infos(cycle_infos)
        task_ids = self.label_studio_api_manager.export_tasks_into_project(data=export_infos)
        metadata_ids = [cycle_info.metadata_id for cycle_info in cycle_infos]
        task_infos = []
        for task_id, metadata_id in zip(task_ids, metadata_ids):
            task_infos.append(
                LabelStudioTaskInfo(
                    task_id=task_id,
                    metadata_id=metadata_id,
                    attribute=URLMetadataAttributeType.RELEVANT,
                    task_status=LabelStudioTaskStatus.PENDING
                )
            )
        await self.adb_client.add_label_studio_task_infos(task_infos)

    async def get_cycle_infos(self) -> list[RelevanceLabelStudioInputCycleInfo]:
        cycle_infos = await self.adb_client.get_info_for_relevance_label_studio_input_cycle()
        return cycle_infos

