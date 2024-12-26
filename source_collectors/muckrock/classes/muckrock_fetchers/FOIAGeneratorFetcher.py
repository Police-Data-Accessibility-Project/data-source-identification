from source_collectors.muckrock.classes.muckrock_fetchers.FOIAFetchManager import FOIAFetchManager
from source_collectors.muckrock.classes.fetch_requests.FOIALoopFetchRequest import FOIALoopFetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockNextFetcher import MuckrockGeneratorFetcher


class FOIAGeneratorFetcher(MuckrockGeneratorFetcher):

    def __init__(self, initial_request: FOIALoopFetchRequest):
        super().__init__(initial_request)
        self.ffm = FOIAFetchManager()

    def process_results(self, results: list[dict]):
        self.ffm.process_results(results)
        return (f"Loop {self.ffm.loop_count}: "
                f"Found {self.ffm.num_found_last_loop} FOIA records;"
                f"{self.ffm.num_found} FOIA records found total.")
