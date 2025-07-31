from random import randint
from typing import final

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.agency import AgencyCommand


@final
class AgencyUserSuggestionsCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        user_id: int | None = None,
        agency_annotation_info: URLAgencyAnnotationPostInfo | None = None
    ):
        super().__init__()
        if user_id is None:
            user_id = randint(1, 99999999)
        self.url_id = url_id
        self.user_id = user_id
        self.agency_annotation_info = agency_annotation_info

    async def run(self) -> None:
        if self.agency_annotation_info is None:
            agency_annotation_info = URLAgencyAnnotationPostInfo(
                suggested_agency=await self.run_command(AgencyCommand())
            )
        else:
            agency_annotation_info = self.agency_annotation_info
        await self.adb_client.add_agency_manual_suggestion(
            agency_id=agency_annotation_info.suggested_agency,
            url_id=self.url_id,
            user_id=self.user_id,
            is_new=agency_annotation_info.is_new
        )
