from src.core.tasks.url.operators.probe.queries.insert_redirects.models.url_response_map import URLResponseMapping
from src.core.tasks.url.operators.probe.queries.urls.exist.model import UrlExistsResult
from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic


def convert_url_response_mapping_to_web_metadata_list(
    url_response_mappings: list[URLResponseMapping]
) -> list[URLWebMetadataPydantic]:
    results: list[URLWebMetadataPydantic] = []
    for url_response_mapping in url_response_mappings:
        response = url_response_mapping.response
        web_metadata_object = URLWebMetadataPydantic(
            url_id=url_response_mapping.url_mapping.url_id,
            accessed=response.status_code is not None,
            status_code=response.status_code,
            content_type=response.content_type,
            error_message=response.error
        )
        results.append(web_metadata_object)
    return results


def convert_to_url_mappings(url_exists_results: list[UrlExistsResult]) -> list[URLMapping]:
    return [
        URLMapping(
            url=url_exists_result.url,
            url_id=url_exists_result.url_id
        ) for url_exists_result in url_exists_results
    ]


def convert_to_url_insert_models(urls: list[str]) -> list[URLInsertModel]:
    results = []
    for url in urls:
        results.append(
            URLInsertModel(
                url=url,
                source=URLSource.REDIRECT
            )
        )
    return results

def convert_tdo_to_url_response_mappings(tdos: list[URLProbeTDO]) -> list[URLResponseMapping]:
    results = []
    for tdo in tdos:
        results.append(
            URLResponseMapping(
                url_mapping=tdo.url_mapping,
                response=tdo.response.response.source
            )
        )
    return results