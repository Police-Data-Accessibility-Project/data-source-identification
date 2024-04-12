from util.db_manager import DBManager


class GoogleSearchQueueManager:

    def __init__(
            self,
            database_manager: DBManager,
    ):
        self.database_manager = database_manager
        self.quota_exceeded = False

    def can_search(self) -> bool:
        return not self.quota_exceeded

    