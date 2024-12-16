from datasets import tqdm

from source_collectors.muckrock.constants import BASE_MUCKROCK_URL
from source_collectors.muckrock.muckrock_fetchers.MuckrockFetcher import FetchRequest
from source_collectors.muckrock.muckrock_fetchers.MuckrockLoopFetcher import MuckrockLoopFetcher

class FOIALoopFetchRequest(FetchRequest):
    jurisdiction: int

class FOIALoopFetcher(MuckrockLoopFetcher):

    def __init__(self, initial_request: FOIALoopFetchRequest):
        super().__init__(initial_request)
        self.pbar_records = tqdm(
            desc="Fetching FOIA records",
            unit="record",
        )
        self.num_found = 0
        self.results = []

    def process_results(self, results: list[dict]):
        self.results.extend(results)

    def build_url(self, request: FOIALoopFetchRequest):
        return f"{BASE_MUCKROCK_URL}/foia/?status=done&jurisdiction={request.jurisdiction}"

    def report_progress(self):
        old_num_found = self.num_found
        self.num_found = len(self.results)
        difference = self.num_found - old_num_found
        self.pbar_records.update(difference)
