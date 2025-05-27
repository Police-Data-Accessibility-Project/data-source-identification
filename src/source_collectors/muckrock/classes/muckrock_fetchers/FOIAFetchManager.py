from src.source_collectors.muckrock.classes.fetch_requests.FOIALoopFetchRequest import FOIALoopFetchRequest
from src.source_collectors.muckrock.constants import BASE_MUCKROCK_URL


class FOIAFetchManager:

    def __init__(self):
        self.num_found = 0
        self.loop_count = 0
        self.num_found_last_loop = 0
        self.results = []

    def build_url(self, request: FOIALoopFetchRequest):
        return f"{BASE_MUCKROCK_URL}/foia/?status=done&jurisdiction={request.jurisdiction}"

    def process_results(self, results: list[dict]):
        self.loop_count += 1
        self.num_found_last_loop = len(results)
        self.results.extend(results)
        self.num_found += len(results)