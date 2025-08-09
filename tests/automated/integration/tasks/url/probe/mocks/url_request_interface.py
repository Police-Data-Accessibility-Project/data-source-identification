from src.external.url_request.probe.models.wrapper import URLProbeResponseOuterWrapper


class MockURLRequestInterface:

    def __init__(
        self,
        response_or_responses: URLProbeResponseOuterWrapper | list[URLProbeResponseOuterWrapper]
    ):
        if not isinstance(response_or_responses, list):
            responses = [response_or_responses]
        else:
            responses = response_or_responses

        self._url_to_response = {
            response.original_url: response for response in responses
        }

    async def probe_urls(self, urls: list[str]) -> list[URLProbeResponseOuterWrapper]:
        return [
            self._url_to_response[url] for url in urls
        ]
