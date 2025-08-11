from datetime import datetime

from src.collectors.enums import URLStatus
from src.db.dtos.url.insert import InsertURLsInfo
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.annotate import AnnotateCommand
from tests.helpers.data_creator.commands.impl.html_data import HTMLDataCreatorCommand
from tests.helpers.data_creator.commands.impl.urls import URLsDBDataCreatorCommand
from tests.helpers.data_creator.commands.impl.urls_v2.response import URLsV2Response
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2
from tests.helpers.data_creator.models.creation_info.url import URLCreationInfo


class URLsV2Command(DBDataCreatorCommandBase):

    def __init__(
        self,
        parameters: list[TestURLCreationParameters],
        batch_id: int | None = None,
        created_at: datetime | None = None
    ):
        super().__init__()
        self.parameters = parameters
        self.batch_id = batch_id
        self.created_at = created_at

    async def run(self) -> URLsV2Response:
        urls_by_status: dict[URLStatus, URLCreationInfo] = {}
        urls_by_order: list[URLCreationInfo] = []
        # Create urls
        for url_parameters in self.parameters:
            command = URLsDBDataCreatorCommand(
                batch_id=self.batch_id,
                url_count=url_parameters.count,
                status=url_parameters.status,
                created_at=self.created_at
            )
            iui: InsertURLsInfo = self.run_command_sync(command)
            url_ids = [iui.url_id for iui in iui.url_mappings]
            if url_parameters.with_html_content:
                command = HTMLDataCreatorCommand(
                    url_ids=url_ids
                )
                await self.run_command(command)
            if url_parameters.annotation_info.has_annotations():
                for url_id in url_ids:
                    await self.run_command(
                        AnnotateCommand(
                            url_id=url_id,
                            annotation_info=url_parameters.annotation_info
                        )
                    )

            creation_info = URLCreationInfo(
                url_mappings=iui.url_mappings,
                outcome=url_parameters.status,
                annotation_info=url_parameters.annotation_info if url_parameters.annotation_info.has_annotations() else None
            )
            urls_by_order.append(creation_info)
            urls_by_status[url_parameters.status] = creation_info

        return URLsV2Response(
            urls_by_status=urls_by_status,
            urls_by_order=urls_by_order
        )
