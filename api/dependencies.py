from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from core.SourceCollectorCore import SourceCollectorCore

core_logger = CoreLogger()
db_client = DatabaseClient()
source_collector_core = SourceCollectorCore(core_logger=core_logger, db_client=db_client)


def get_core() -> SourceCollectorCore:
    return source_collector_core
