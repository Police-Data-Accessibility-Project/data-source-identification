from src.collectors.impl.muckrock.fetch_requests.jurisdiction_loop import JurisdictionLoopFetchRequest
from src.collectors.impl.muckrock.constants import BASE_MUCKROCK_URL


class JurisdictionFetchManager:

    def __init__(self, town_names: list[str]):
        self.town_names = town_names
        self.num_jurisdictions_found = 0
        self.total_found = 0
        self.jurisdictions = {}

    def build_url(self, request: JurisdictionLoopFetchRequest) -> str:
        return f"{BASE_MUCKROCK_URL}/jurisdiction/?level={request.level}&parent={request.parent}"

    def process_results(self, results: list[dict]):
        for item in results:
            if item["name"] in self.town_names:
                self.jurisdictions[item["name"]] = item["id"]
                self.total_found += 1
        self.num_jurisdictions_found = len(self.jurisdictions)
        return f"Found {self.num_jurisdictions_found} jurisdictions; {self.total_found} entries found total."
