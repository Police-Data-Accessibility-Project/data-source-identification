import time

from pydantic import BaseModel

from collector_manager.enums import CollectorType
from core.SourceCollectorCore import SourceCollectorCore


def run_collector_and_wait_for_completion(
    collector_type: CollectorType,
    core: SourceCollectorCore,
    dto: BaseModel
):
    collector_name = collector_type.value
    response = core.initiate_collector(
        collector_type=collector_type,
        dto=dto
    )
    assert response == f"Started {collector_name} collector with CID: 1"
    response = core.get_status(1)
    while response == f"1 ({collector_name}) - RUNNING":
        time.sleep(1)
        response = core.get_status(1)
    assert response == f"1 ({collector_name}) - COMPLETED", response
    # TODO: Change this logic, since collectors close automatically
    response = core.close_collector(1)
    assert response.message == "Collector closed and data harvested successfully."
