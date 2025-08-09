from src.core.tasks.url.operators.probe.tdo import URLProbeTDO
from src.db.dtos.url.mapping import URLMapping
from src.external.url_request.probe.models.redirect import URLProbeRedirectResponsePair


def extract_response_pairs(tdos: list[URLProbeTDO]) -> list[URLProbeRedirectResponsePair]:
    results = []
    for tdo in tdos:
        if not tdo.response.is_redirect:
            raise ValueError(f"Expected {tdo.url_mapping.url} to be a redirect.")

        response: URLProbeRedirectResponsePair = tdo.response.response
        if not isinstance(response, URLProbeRedirectResponsePair):
            raise ValueError(f"Expected {tdo.url_mapping.url} to be {URLProbeRedirectResponsePair.__name__}.")
        results.append(response)
    return results
