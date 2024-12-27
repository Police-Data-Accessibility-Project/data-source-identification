import time

import pytest

from collector_manager.enums import CollectorType, URLOutcome
from core.CoreInterface import CoreInterface
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus


def test_example_collector_lifecycle(test_core_interface):
    """
    Test the flow of an example collector, which generates fake urls
    and saves them to the database
    """
    ci = test_core_interface
    db_client = ci.core.db_client
    config = {
            "example_field": "example_value"
        }
    response = ci.start_collector(
        collector_type=CollectorType.EXAMPLE,
        config=config
    )
    assert response == "Started example_collector collector with CID: 1"

    response = ci.get_status(1)
    assert response == "1 (example_collector) - RUNNING"
    time.sleep(1.5)
    response = ci.get_status(1)
    assert response == "1 (example_collector) - COMPLETED"
    response = ci.close_collector(1)
    assert response == "Collector closed and data harvested successfully."

    batch_info = db_client.get_batch_by_id(1)
    assert batch_info.strategy == "example_collector"
    assert batch_info.status == BatchStatus.COMPLETE
    assert batch_info.count == 2
    assert batch_info.parameters == config
    assert batch_info.compute_time > 1

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) == 2
    assert url_infos[0].outcome == URLOutcome.PENDING


