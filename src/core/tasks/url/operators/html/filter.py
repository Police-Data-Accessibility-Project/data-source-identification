from http import HTTPStatus

from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO


async def filter_just_urls(tdos: list[UrlHtmlTDO]):
    return [task_info.url_info.url for task_info in tdos]

async def filter_404_subset(tdos: list[UrlHtmlTDO]) -> list[UrlHtmlTDO]:
    return [
        tdo for tdo in tdos
        if tdo.url_response_info.status == HTTPStatus.NOT_FOUND
    ]
