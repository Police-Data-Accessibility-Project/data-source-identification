import time

from tests.source_collector.helpers.common_test_procedures import run_collector_and_wait_for_completion
from tests.source_collector.helpers.constants import ALLEGHENY_COUNTY_TOWN_NAMES, ALLEGHENY_COUNTY_MUCKROCK_ID
from collector_manager.enums import CollectorType
from core.enums import BatchStatus


def test_muckrock_simple_search_collector_lifecycle(test_core_interface):
    ci = test_core_interface
    db_client = ci.core.db_client

    config = {
        "search_string": "police",
        "max_results": 10
    }
    run_collector_and_wait_for_completion(
        collector_type=CollectorType.MUCKROCK_SIMPLE_SEARCH,
        ci=ci,
        config=config
    )

    batch_info = db_client.get_batch_by_id(1)
    assert batch_info.strategy == "muckrock_simple_search"
    assert batch_info.status == BatchStatus.COMPLETE
    assert batch_info.count >= 10

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) >= 10

def test_muckrock_county_level_search_collector_lifecycle(test_core_interface):
    ci = test_core_interface
    db_client = ci.core.db_client

    config = {
        "parent_jurisdiction_id": ALLEGHENY_COUNTY_MUCKROCK_ID,
        "town_names": ALLEGHENY_COUNTY_TOWN_NAMES
    }
    run_collector_and_wait_for_completion(
        collector_type=CollectorType.MUCKROCK_COUNTY_SEARCH,
        ci=ci,
        config=config
    )

    batch_info = db_client.get_batch_by_id(1)
    assert batch_info.strategy == "muckrock_county_search"
    assert batch_info.status == BatchStatus.COMPLETE
    assert batch_info.count >= 10

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) >= 10

def test_muckrock_full_search_collector_lifecycle(test_core_interface):
    ci = test_core_interface
    db_client = ci.core.db_client

    config = {
        "start_page": 1,
        "pages": 2
    }
    run_collector_and_wait_for_completion(
        collector_type=CollectorType.MUCKROCK_ALL_SEARCH,
        ci=ci,
        config=config
    )

    batch_info = db_client.get_batch_by_id(1)
    assert batch_info.strategy == CollectorType.MUCKROCK_ALL_SEARCH.value
    assert batch_info.status == BatchStatus.COMPLETE
    assert batch_info.count >= 1

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) >= 1