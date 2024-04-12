from google_searcher.google_searcher import GoogleSearcher, QuotaExceededError, GoogleSearchResult
from util.db_manager import DBManager
from dataclasses import dataclass

SQL_GET_NEXT_IN_QUEUE = """
    SELECT search_id, search_query
    FROM public.search_queue
    WHERE executed_datetime is Null
    ORDER BY search_id asc
    LIMIT ?;
"""


@dataclass
class PendingSearch:
    search_id: str
    search_query: str


class GoogleSearchQueueManager:

    def __init__(
            self,
            database_manager: DBManager,
            google_searcher: GoogleSearcher
    ):
        self.database_manager = database_manager
        self.google_searcher = google_searcher
        self.quota_exceeded = False

    def get_next_in_queue(self, limit: int = 100) -> list[PendingSearch]:
        rows = self.database_manager.execute(SQL_GET_NEXT_IN_QUEUE, limit)
        pending_searches = []
        for row in rows:
            pending_searches.append(PendingSearch(*row))
        return pending_searches

    def upload_search_results(self, search_id: str, results: list[GoogleSearchResult]):
        self.database_manager.executemany(
            "INSERT INTO search_results (search_id, url, title, snippet) VALUES (?, ?, ?, ?)",
            [(search_id, result.url, result.title, result.snippet) for result in results])

    def run_searches_from_queue(self):
        pending_searches = self.get_next_in_queue()
        for pending_search in pending_searches:
            try:
                results = self.google_searcher.search(pending_search.search_query)
                self.upload_search_results(pending_search.search_id, results)
            except QuotaExceededError:
                self.quota_exceeded = True
                return

    def run_searches_until_quota_exceeded(self):
        while not self.quota_exceeded:
            self.run_searches_from_queue()
