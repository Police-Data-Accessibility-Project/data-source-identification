from http import HTTPStatus

from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase


class URLMetadataCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_ids: list[int],
        content_type: str = "text/html",
        status_code: int = HTTPStatus.OK.value
    ):
        super().__init__()
        self.url_ids = url_ids
        self.content_type = content_type
        self.status_code = status_code

    async def run(self) -> None:
        url_metadata_infos = []
        for url_id in self.url_ids:
            url_metadata = URLWebMetadataPydantic(
                url_id=url_id,
                accessed=True,
                status_code=self.status_code,
                content_type=self.content_type,
                error_message=None
            )
            url_metadata_infos.append(url_metadata)
        await self.adb_client.bulk_insert(url_metadata_infos)