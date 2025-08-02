from http import HTTPStatus

from src.core.tasks.url.operators.html.models.subsets.error_404 import ErrorSubsets
from src.core.tasks.url.operators.html.models.subsets.success_error import SuccessErrorSubset
from src.core.tasks.url.operators.html.tdo import UrlHtmlTDO


async def get_just_urls(tdos: list[UrlHtmlTDO]):
    return [task_info.url_info.url for task_info in tdos]


async def separate_success_and_error_subsets(
    tdos: list[UrlHtmlTDO]
) -> SuccessErrorSubset:
    errored_tdos = []
    successful_tdos = []
    for tdto in tdos:
        if not tdto.url_response_info.success:
            errored_tdos.append(tdto)
        else:
            successful_tdos.append(tdto)
    return SuccessErrorSubset(
        success=successful_tdos,
        error=errored_tdos
    )


async def separate_404_and_non_404_subsets(
    tdos: list[UrlHtmlTDO]
) -> ErrorSubsets:
    tdos_error = []
    tdos_404 = []
    for tdo in tdos:
        if tdo.url_response_info.status is None:
            tdos_error.append(tdo)
            continue
        if tdo.url_response_info.status == HTTPStatus.NOT_FOUND:
            tdos_404.append(tdo)
        else:
            tdos_error.append(tdo)
    return ErrorSubsets(
        not_404=tdos_error,
        is_404=tdos_404
    )
