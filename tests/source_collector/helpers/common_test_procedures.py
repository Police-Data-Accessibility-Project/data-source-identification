import time

from collector_manager.enums import CollectorType
from core.CoreInterface import CoreInterface


def run_collector_and_wait_for_completion(
    collector_type: CollectorType,
    ci: CoreInterface,
    config: dict
):
    collector_name = collector_type.value
    response = ci.start_collector(
        collector_type=collector_type,
        config=config
    )
    assert response == f"Started {collector_name} collector with CID: 1"
    response = ci.get_status(1)
    while response == f"1 ({collector_name}) - RUNNING":
        time.sleep(1)
        response = ci.get_status(1)
    assert response == f"1 ({collector_name}) - COMPLETED", response
    response = ci.close_collector(1)
    assert response.message == "Collector closed and data harvested successfully."
