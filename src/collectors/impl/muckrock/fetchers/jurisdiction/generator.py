from src.collectors.impl.muckrock.fetch_requests.jurisdiction_loop import JurisdictionLoopFetchRequest
from src.collectors.impl.muckrock.fetchers.jurisdiction.manager import JurisdictionFetchManager
from src.collectors.impl.muckrock.fetchers.templates.generator import MuckrockGeneratorFetcher


class JurisdictionGeneratorFetcher(MuckrockGeneratorFetcher):

    def __init__(self, initial_request: JurisdictionLoopFetchRequest):
        super().__init__(initial_request)
        self.jfm = JurisdictionFetchManager(town_names=initial_request.town_names)

    def build_url(self, request: JurisdictionLoopFetchRequest) -> str:
        return self.jfm.build_url(request)

    def process_results(self, results: list[dict]):
        return self.jfm.process_results(results)

