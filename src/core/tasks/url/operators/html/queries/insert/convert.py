from http import HTTPStatus

from src.core.tasks.url.operators.html.content_info_getter import HTMLContentInfoGetter
from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.models.instantiations.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.models.instantiations.url.html.compressed.pydantic import URLCompressedHTMLPydantic
from src.db.models.instantiations.url.scrape_info.enums import ScrapeStatus
from src.db.models.instantiations.url.scrape_info.pydantic import URLScrapeInfoInsertModel
from src.db.utils.compression import compress_html
from src.external.url_request.dtos.url_response import URLResponseInfo


def convert_to_compressed_html(tdos: list[UrlHtmlTDO]) -> list[URLCompressedHTMLPydantic]:
    models = []
    for tdo in tdos:
        if tdo.url_response_info.status != HTTPStatus.OK:
            continue
        model = URLCompressedHTMLPydantic(
            url_id=tdo.url_info.id,
            compressed_html=compress_html(tdo.url_response_info.html)
        )
        models.append(model)
    return models



def _convert_to_html_content_info_getter(tdo: UrlHtmlTDO) -> HTMLContentInfoGetter:
    return HTMLContentInfoGetter(
        response_html_info=tdo.html_tag_info,
        url_id=tdo.url_info.id
    )

def convert_to_html_content_info_list(tdos: list[UrlHtmlTDO]) -> list[URLHTMLContentInfo]:
    html_content_infos = []
    for tdo in tdos:
        if tdo.url_response_info.status != HTTPStatus.OK:
            continue
        hcig = _convert_to_html_content_info_getter(tdo)
        results = hcig.get_all_html_content()
        html_content_infos.extend(results)
    return html_content_infos

def get_scrape_status(response_info: URLResponseInfo) -> ScrapeStatus:
    if response_info.success:
        return ScrapeStatus.SUCCESS
    return ScrapeStatus.ERROR

def convert_to_scrape_infos(tdos: list[UrlHtmlTDO]) -> list[URLScrapeInfoInsertModel]:
    models = []
    for tdo in tdos:
        model = URLScrapeInfoInsertModel(
            url_id=tdo.url_info.id,
            status=get_scrape_status(tdo.url_response_info)
        )
        models.append(model)
    return models

def convert_to_url_errors(
    tdos: list[UrlHtmlTDO],
    task_id: int
) -> list[URLErrorPydanticInfo]:
    models = []
    for tdo in tdos:
        if tdo.url_response_info.success:
            continue
        model = URLErrorPydanticInfo(
            url_id=tdo.url_info.id,
            error=tdo.url_response_info.exception,
            task_id=task_id
        )
        models.append(model)
    return models