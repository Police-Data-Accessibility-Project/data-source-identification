import pendulum
import pytest

from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus, RecordType, SuggestedStatus
from tests.helpers.test_batch_creation_parameters import TestBatchCreationParameters, TestURLCreationParameters, \
    AnnotationInfo


@pytest.mark.asyncio
async def test_get_batches_aggregated_metrics(api_test_helper):
    ath = api_test_helper
    # Create successful batches with URLs of different statuses
    all_params = []
    for i in range(3):
        params = TestBatchCreationParameters(
            strategy=CollectorType.MANUAL,
            urls=[
                TestURLCreationParameters(
                    count=1,
                    status=URLStatus.PENDING
                ),
                TestURLCreationParameters(
                    count=2,
                    status=URLStatus.SUBMITTED
                ),
                TestURLCreationParameters(
                    count=3,
                    status=URLStatus.NOT_RELEVANT
                ),
                TestURLCreationParameters(
                    count=4,
                    status=URLStatus.ERROR
                ),
                TestURLCreationParameters(
                    count=5,
                    status=URLStatus.VALIDATED
                )
            ]
        )
        all_params.append(params)


    # Create failed batches
    for i in range(2):
        params = TestBatchCreationParameters(
            outcome=BatchStatus.ERROR
        )
        all_params.append(params)

    for params in all_params:
        await ath.db_data_creator.batch_v2(params)

    dto = await ath.request_validator.get_batches_aggregated_metrics()
    assert dto.total_batches == 5
    inner_dto_example = dto.by_strategy[CollectorType.EXAMPLE]
    assert inner_dto_example.count_urls == 0
    assert inner_dto_example.count_successful_batches == 0
    assert inner_dto_example.count_failed_batches == 2
    assert inner_dto_example.count_urls_pending == 0
    assert inner_dto_example.count_urls_submitted == 0
    assert inner_dto_example.count_urls_rejected == 0
    assert inner_dto_example.count_urls_errors == 0
    assert inner_dto_example.count_urls_validated == 0

    inner_dto_manual = dto.by_strategy[CollectorType.MANUAL]
    assert inner_dto_manual.count_urls == 45
    assert inner_dto_manual.count_successful_batches == 3
    assert inner_dto_manual.count_failed_batches == 0
    assert inner_dto_manual.count_urls_pending == 3
    assert inner_dto_manual.count_urls_submitted == 6
    assert inner_dto_manual.count_urls_rejected == 9
    assert inner_dto_manual.count_urls_errors == 12
    assert inner_dto_manual.count_urls_validated == 15


@pytest.mark.asyncio
async def test_get_batches_breakdown_metrics(api_test_helper):
    # Create a different batch for each month, with different URLs
    today = pendulum.parse('2021-01-01')
    ath = api_test_helper

    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)
    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.EXAMPLE,
        outcome=BatchStatus.ERROR,
        created_at=today.subtract(weeks=1),
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)
    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        created_at=today.subtract(weeks=2),
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.NOT_RELEVANT
            ),
            TestURLCreationParameters(
                count=4,
                status=URLStatus.ERROR
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.VALIDATED
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    dto_1 = await ath.request_validator.get_batches_breakdown_metrics(
        page=1
    )
    assert len(dto_1.batches) == 3
    dto_batch_1 = dto_1.batches[2]
    assert dto_batch_1.batch_id == batch_1.batch_id
    assert dto_batch_1.strategy == CollectorType.MANUAL
    assert dto_batch_1.status == BatchStatus.READY_TO_LABEL
    assert pendulum.instance(dto_batch_1.created_at) > today
    assert dto_batch_1.count_url_total == 3
    assert dto_batch_1.count_url_pending == 1
    assert dto_batch_1.count_url_submitted == 2
    assert dto_batch_1.count_url_rejected == 0
    assert dto_batch_1.count_url_error == 0
    assert dto_batch_1.count_url_validated == 0

    dto_batch_2 = dto_1.batches[1]
    assert dto_batch_2.batch_id == batch_2.batch_id
    assert dto_batch_2.status == BatchStatus.ERROR
    assert dto_batch_2.strategy == CollectorType.EXAMPLE
    assert pendulum.instance(dto_batch_2.created_at) == today.subtract(weeks=1)
    assert dto_batch_2.count_url_total == 0
    assert dto_batch_2.count_url_submitted == 0
    assert dto_batch_2.count_url_pending == 0
    assert dto_batch_2.count_url_rejected == 0
    assert dto_batch_2.count_url_error == 0
    assert dto_batch_2.count_url_validated == 0

    dto_batch_3 = dto_1.batches[0]
    assert dto_batch_3.batch_id == batch_3.batch_id
    assert dto_batch_3.status == BatchStatus.READY_TO_LABEL
    assert dto_batch_3.strategy == CollectorType.AUTO_GOOGLER
    assert pendulum.instance(dto_batch_3.created_at) == today.subtract(weeks=2)
    assert dto_batch_3.count_url_total == 12
    assert dto_batch_3.count_url_pending == 0
    assert dto_batch_3.count_url_submitted == 0
    assert dto_batch_3.count_url_rejected == 3
    assert dto_batch_3.count_url_error == 4
    assert dto_batch_3.count_url_validated == 5

    dto_2 = await ath.request_validator.get_batches_breakdown_metrics(
        page=2
    )
    assert len(dto_2.batches) == 0

@pytest.mark.asyncio
async def test_get_urls_breakdown_submitted_metrics(api_test_helper):
    # Create URLs with submitted status, broken down in different amounts by different weeks
    # And ensure the URLs are
    today = pendulum.parse('2021-01-01')
    ath = api_test_helper

    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)
    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.EXAMPLE,
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.SUBMITTED
            )
        ],
        created_at=today.subtract(weeks=1),
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)
    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        created_at=today.subtract(weeks=1),
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.SUBMITTED
            ),
            TestURLCreationParameters(
                count=4,
                status=URLStatus.ERROR
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.VALIDATED
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    dto = await ath.request_validator.get_urls_breakdown_submitted_metrics()
    assert len(dto.entries) == 2

    entry_1 = dto.entries[0]
    assert entry_1.count_submitted == 6

    entry_2 = dto.entries[1]
    assert entry_2.count_submitted == 2


@pytest.mark.asyncio
async def test_get_urls_breakdown_pending_metrics(api_test_helper):
    # Build URLs, broken down into three separate weeks,
    # with each week having a different number of pending URLs
    # with a different number of kinds of annotations per URLs


    today = pendulum.parse('2021-01-01')
    ath = api_test_helper

    agency_id = await ath.db_data_creator.agency()
    # Additionally, add some URLs that are submitted,
    # validated, errored, and ensure they are not counted
    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)
    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.EXAMPLE,
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.RELEVANT,
                    user_record_type=RecordType.CALLS_FOR_SERVICE
                )
            )
        ],
        created_at=today.subtract(weeks=1),
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)
    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        created_at=today.subtract(weeks=1),
        urls=[
            TestURLCreationParameters(
                count=3,
                status=URLStatus.SUBMITTED
            ),
            TestURLCreationParameters(
                count=4,
                status=URLStatus.ERROR
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.RELEVANT,
                    user_record_type=RecordType.INCARCERATION_RECORDS,
                    user_agency=agency_id
                )
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    dto = await ath.request_validator.get_urls_breakdown_pending_metrics()
    assert len(dto.entries) == 2

    entry_1 = dto.entries[0]
    assert entry_1.count_pending_total == 8
    assert entry_1.count_pending_relevant_user == 8
    assert entry_1.count_pending_record_type_user == 8
    assert entry_1.count_pending_agency_user == 5

    entry_2 = dto.entries[1]
    assert entry_2.count_pending_total == 1
    assert entry_2.count_pending_relevant_user == 1
    assert entry_2.count_pending_record_type_user == 0
    assert entry_2.count_pending_agency_user == 0

@pytest.mark.asyncio
async def test_get_urls_aggregate_metrics(api_test_helper):
    ath = api_test_helper
    today = pendulum.parse('2021-01-01')

    batch_0_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        created_at=today.subtract(days=1),
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
            ),
        ]
    )
    batch_0 = await ath.db_data_creator.batch_v2(batch_0_params)
    oldest_url_id = batch_0.url_creation_infos[URLStatus.PENDING].url_mappings[0].url_id


    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)

    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        urls=[
            TestURLCreationParameters(
                count=4,
                status=URLStatus.PENDING,
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.ERROR
            ),
            TestURLCreationParameters(
                count=1,
                status=URLStatus.VALIDATED
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.NOT_RELEVANT
            ),
        ]
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)

    dto = await ath.request_validator.get_urls_aggregated_metrics()

    assert dto.oldest_pending_url_id == oldest_url_id
    assert dto.oldest_pending_url_created_at == today.subtract(days=1).in_timezone('UTC').naive()
    assert dto.count_urls_pending == 6
    assert dto.count_urls_rejected == 5
    assert dto.count_urls_errors == 2
    assert dto.count_urls_validated == 1
    assert dto.count_urls_submitted == 2
    assert dto.count_urls_total == 16



@pytest.mark.asyncio
async def test_get_backlog_metrics(api_test_helper):
    today = pendulum.parse('2021-01-01')

    ath = api_test_helper
    adb_client = ath.adb_client()


    # Populate the backlog table and test that backlog metrics returned on a monthly basis
    # Ensure that multiple days in each month are added to the backlog table, with different values


    batch_1_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.SUBMITTED
            ),
        ]
    )
    batch_1 = await ath.db_data_creator.batch_v2(batch_1_params)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=3).naive()
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=2, days=3).naive()
    )

    batch_2_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        urls=[
            TestURLCreationParameters(
                count=4,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=2,
                status=URLStatus.ERROR
            ),
        ]
    )
    batch_2 = await ath.db_data_creator.batch_v2(batch_2_params)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=2).naive()
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=1, days=4).naive()
    )

    batch_3_params = TestBatchCreationParameters(
        strategy=CollectorType.AUTO_GOOGLER,
        urls=[
            TestURLCreationParameters(
                count=7,
                status=URLStatus.PENDING,
                annotation_info=AnnotationInfo(
                    user_relevant=SuggestedStatus.NOT_RELEVANT
                )
            ),
            TestURLCreationParameters(
                count=5,
                status=URLStatus.VALIDATED
            ),
        ]
    )
    batch_3 = await ath.db_data_creator.batch_v2(batch_3_params)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=1).naive()
    )

    dto = await ath.request_validator.get_backlog_metrics()

    assert len(dto.entries) == 3

    # Test that the count closest to the beginning of the month is returned for each month
    assert dto.entries[0].count_pending_total == 1
    assert dto.entries[1].count_pending_total == 5
    assert dto.entries[2].count_pending_total == 12