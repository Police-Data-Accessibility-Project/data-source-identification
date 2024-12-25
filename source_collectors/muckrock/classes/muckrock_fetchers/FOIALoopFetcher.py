from datasets import tqdm

from source_collectors.muckrock.classes.fetch_requests.FOIALoopFetchRequest import FOIALoopFetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers.FOIAFetchManager import FOIAFetchManager
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockLoopFetcher import MuckrockLoopFetcher


class FOIALoopFetcher(MuckrockLoopFetcher):

    def __init__(self, initial_request: FOIALoopFetchRequest):
        super().__init__(initial_request)
        self.pbar_records = tqdm(
            desc="Fetching FOIA records",
            unit="record",
        )
        self.ffm = FOIAFetchManager()

    def process_results(self, results: list[dict]):
        self.ffm.process_results(results)

    def build_url(self, request: FOIALoopFetchRequest):
        return self.ffm.build_url(request)

    def report_progress(self):
        self.pbar_records.update(self.ffm.num_found_last_loop)
