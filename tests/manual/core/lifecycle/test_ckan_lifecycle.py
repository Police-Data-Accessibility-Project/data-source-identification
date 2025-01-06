import api.dependencies
from tests.automated.core.helpers.common_test_procedures import run_collector_and_wait_for_completion

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.enums import CollectorType
from core.enums import BatchStatus
from source_collectors.ckan.search_terms import group_search, package_search, organization_search


def test_ckan_lifecycle(test_core):
    ci = test_core
    db_client = api.dependencies.db_client

    config = {
        "package_search": package_search,
        "group_search": group_search,
        "organization_search": organization_search
    }
    run_collector_and_wait_for_completion(
        collector_type=CollectorType.CKAN,
        ci=ci,
        config=config
    )

    batch_info: BatchInfo = db_client.get_batch_by_id(1)
    assert batch_info.strategy == "ckan"
    assert batch_info.status == BatchStatus.COMPLETE
    assert batch_info.total_url_count >= 3000

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) >= 2500