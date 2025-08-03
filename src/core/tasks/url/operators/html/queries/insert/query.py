from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.html.queries.insert.convert import convert_to_compressed_html, \
    convert_to_html_content_info_list, convert_to_scrape_infos, convert_to_url_errors
from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class InsertURLHTMLInfoQueryBuilder(QueryBuilderBase):

    def __init__(self, tdos: list[UrlHtmlTDO], task_id: int):
        super().__init__()
        self.tdos = tdos
        self.task_id = task_id

    async def run(self, session: AsyncSession) -> None:
        compressed_html_models = convert_to_compressed_html(self.tdos)
        url_html_content_list = convert_to_html_content_info_list(self.tdos)
        scrape_info_list = convert_to_scrape_infos(self.tdos)
        url_errors = convert_to_url_errors(self.tdos, task_id=self.task_id)

        for models in [
            compressed_html_models,
            url_html_content_list,
            scrape_info_list,
            url_errors
        ]:
            await sh.bulk_insert(session, models=models)


