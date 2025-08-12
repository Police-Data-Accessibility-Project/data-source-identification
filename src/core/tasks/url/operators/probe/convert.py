from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic


def convert_tdo_to_web_metadata_list(tdos: list[URLProbeTDO]) -> list[URLWebMetadataPydantic]:
    results: list[URLWebMetadataPydantic] = []
    for tdo in tdos:
        response = tdo.response.response
        web_metadata_object = URLWebMetadataPydantic(
            url_id=tdo.url_mapping.url_id,
            accessed=response.status_code != 404,
            status_code=response.status_code,
            content_type=response.content_type,
            error_message=response.error
        )
        results.append(web_metadata_object)
    return results

