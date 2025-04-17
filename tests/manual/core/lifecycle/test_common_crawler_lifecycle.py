import time

import api.dependencies
from collector_manager.enums import CollectorType
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus


def test_common_crawler_lifecycle(test_core: SourceCollectorCore):
    core = test_core
    db_client = api.dependencies.db_client

    config = {
        "common_crawl_id": "CC-MAIN-2023-50",
        "url": "*.gov",
        "keyword": "police",
        "start_page": 1,
        "pages": 2
    }
    response = core.start_collector(
        collector_type=CollectorType.COMMON_CRAWLER,
        config=config
    )
    assert response == "Started common_crawler collector with CID: 1"

    response = core.get_status(1)
    while response == "1 (common_crawler) - RUNNING":
        time.sleep(1)
        response = core.get_status(1)

    assert response == "1 (common_crawler) - COMPLETED"
    response = core.close_collector(1)
    assert response == "Collector closed and data harvested successfully."

    batch_info = db_client.get_batch_by_id(1)
    assert batch_info.strategy == "common_crawler"
    assert batch_info.status == BatchStatus.READY_TO_LABEL
    assert batch_info.parameters == config

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) > 0
