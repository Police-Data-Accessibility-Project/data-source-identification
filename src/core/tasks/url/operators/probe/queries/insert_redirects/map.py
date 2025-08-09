from src.core.tasks.url.operators.probe.queries.insert_redirects.models.url_response_map import URLResponseMapping
from src.db.dtos.url.mapping import URLMapping
from src.external.url_request.probe.models.response import URLProbeResponse


def map_url_mappings_to_probe_responses(
    url_mappings: list[URLMapping],
    url_to_probe_responses: dict[str, URLProbeResponse]
) -> list[URLResponseMapping]:
    results = []
    for url_mapping in url_mappings:
        response = url_to_probe_responses[url_mapping.url]
        results.append(
            URLResponseMapping(
                url_mapping=url_mapping,
                response=response
            )
        )
    return results