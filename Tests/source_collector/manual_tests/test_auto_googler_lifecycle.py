import os
import time

import dotenv

from collector_manager.enums import CollectorType
from core.enums import BatchStatus


def test_auto_googler_collector_lifecycle(test_core_interface):
    ci = test_core_interface
    db_client = ci.core.db_client

    dotenv.load_dotenv()
    config = {
        "api_key": os.getenv("GOOGLE_API_KEY"),
        "cse_id": os.getenv("GOOGLE_CSE_ID"),
        "urls_per_result": 10,
        "queries": [
            "Disco Elysium",
            "Dune"
        ]
    }
    response = ci.start_collector(
        collector_type=CollectorType.AUTO_GOOGLER,
        config=config
    )
    assert response == "Started auto_googler collector with CID: 1"

    response = ci.get_status(1)
    while response == "1 (auto_googler) - RUNNING":
        time.sleep(1)
        response = ci.get_status(1)


    assert response == "1 (auto_googler) - COMPLETED"
    response = ci.close_collector(1)
    assert response == "Collector closed and data harvested successfully."

    batch_info = ci.core.db_client.get_batch_by_id(1)
    assert batch_info.strategy == "auto_googler"
    assert batch_info.status == BatchStatus.COMPLETE
    assert batch_info.count == 20

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) == 20
    q1_urls = [url_info.url for url_info in url_infos if url_info.url_metadata["query"] == "Disco Elysium"]
    q2_urls = [url_info.url for url_info in url_infos if url_info.url_metadata["query"] == "Dune"]

    assert len(q1_urls) == len(q2_urls) == 10
