from tqdm import tqdm

from src.collectors.impl.muckrock.fetch_requests.jurisdiction_loop import JurisdictionLoopFetchRequest
from src.collectors.impl.muckrock.fetchers.jurisdiction.manager import JurisdictionFetchManager
from src.collectors.impl.muckrock.fetchers.templates.loop import MuckrockLoopFetcher


class JurisdictionLoopFetcher(MuckrockLoopFetcher):

    def __init__(self, initial_request: JurisdictionLoopFetchRequest):
        super().__init__(initial_request)
        self.jfm = JurisdictionFetchManager(town_names=initial_request.town_names)
        self.pbar_jurisdictions = tqdm(
            total=len(self.jfm.town_names),
            desc="Fetching jurisdictions",
            unit="jurisdiction",
            position=0,
            leave=False
        )
        self.pbar_page = tqdm(
            desc="Processing pages",
            unit="page",
            position=1,
            leave=False
        )

    def build_url(self, request: JurisdictionLoopFetchRequest) -> str:
        return self.jfm.build_url(request)

    def process_results(self, results: list[dict]):
        self.jfm.process_results(results)

    def report_progress(self):
        old_num_jurisdictions_found = self.jfm.num_jurisdictions_found
        self.jfm.num_jurisdictions_found = len(self.jfm.jurisdictions)
        difference = self.jfm.num_jurisdictions_found - old_num_jurisdictions_found
        self.pbar_jurisdictions.update(difference)
        self.pbar_page.update(1)
