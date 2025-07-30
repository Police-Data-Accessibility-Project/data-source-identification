from src.db.dtos.url.html_content import URLHTMLContentInfo, HTMLContentType
from src.db.dtos.url.raw_html import RawHTMLInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.models.clients import DBDataCreatorClientContainer


class HTMLDataCreatorCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_ids: list[int]
    ):
        super().__init__()
        self.url_ids = url_ids

    async def run(self) -> None:
        html_content_infos = []
        raw_html_info_list = []
        for url_id in self.url_ids:
            html_content_infos.append(
                URLHTMLContentInfo(
                    url_id=url_id,
                    content_type=HTMLContentType.TITLE,
                    content="test html content"
                )
            )
            html_content_infos.append(
                URLHTMLContentInfo(
                    url_id=url_id,
                    content_type=HTMLContentType.DESCRIPTION,
                    content="test description"
                )
            )
            raw_html_info = RawHTMLInfo(
                url_id=url_id,
                html="<html></html>"
            )
            raw_html_info_list.append(raw_html_info)

        await self.adb_client.add_raw_html(raw_html_info_list)
        await self.adb_client.add_html_content_infos(html_content_infos)

