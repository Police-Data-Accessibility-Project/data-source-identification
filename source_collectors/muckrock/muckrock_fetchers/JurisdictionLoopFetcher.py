from tqdm import tqdm

from source_collectors.muckrock.constants import BASE_MUCKROCK_URL
from source_collectors.muckrock.muckrock_fetchers.MuckrockFetcher import FetchRequest, MuckrockFetcher
from source_collectors.muckrock.muckrock_fetchers.MuckrockLoopFetcher import MuckrockLoopFetcher


class JurisdictionLoopFetchRequest(FetchRequest):
    level: str
    parent: int
    town_names: list

class JurisdictionLoopFetcher(MuckrockLoopFetcher):

    def __init__(self, initial_request: JurisdictionLoopFetchRequest):
        super().__init__(initial_request)
        self.town_names = initial_request.town_names
        self.pbar_jurisdictions = tqdm(
            total=len(self.town_names),
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
        self.num_found = 0
        self.jurisdictions = {}

    def build_url(self, request: JurisdictionLoopFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/jurisdiction/?level={request.level}&parent={request.parent}"

    def process_results(self, results: list[dict]):
        for item in results:
            if item["name"] in self.town_names:
                self.jurisdictions[item["name"]] = item["id"]

    def report_progress(self):
        old_num_found = self.num_found
        self.num_found = len(self.jurisdictions)
        difference = self.num_found - old_num_found
        self.pbar_jurisdictions.update(difference)
        self.pbar_page.update(1)
