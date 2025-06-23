from src.db.dtos.batch_info import BatchInfo
from src.collectors import CollectorType
from src.core.enums import BatchStatus
from src.collectors.source_collectors.ckan import group_search, package_search, organization_search
from test_automated.integration.core.helpers.common_test_procedures import run_collector_and_wait_for_completion


def test_ckan_lifecycle(test_core):
    ci = test_core
    db_client = src.api.dependencies.db_client

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
    assert batch_info.status == BatchStatus.READY_TO_LABEL
    assert batch_info.total_url_count >= 3000

    url_infos = db_client.get_urls_by_batch(1)
    assert len(url_infos) >= 2500