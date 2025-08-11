from src.collectors.impl.muckrock.fetch_requests import FOIALoopFetchRequest
from src.collectors.impl.muckrock.fetchers.foia.manager import FOIAFetchManager
from src.collectors.impl.muckrock.fetchers.templates.generator import MuckrockGeneratorFetcher


class FOIAGeneratorFetcher(MuckrockGeneratorFetcher):

    def __init__(self, initial_request: FOIALoopFetchRequest):
        super().__init__(initial_request)
        self.ffm = FOIAFetchManager()

    def process_results(self, results: list[dict]):
        self.ffm.process_results(results)
        return (f"Loop {self.ffm.loop_count}: "
                f"Found {self.ffm.num_found_last_loop} FOIA records;"
                f"{self.ffm.num_found} FOIA records found total.")
