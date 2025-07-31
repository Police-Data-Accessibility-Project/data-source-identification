from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientSession

from src.collectors.enums import CollectorType, URLStatus
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.auto_googler import \
    AutoGooglerAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.ckan import CKANAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.common_crawler import \
    CommonCrawlerAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.muckrock import MuckrockAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.no_collector import \
    NoCollectorAgencyIdentificationSubtask
from tests.automated.integration.tasks.url.agency_identification.happy_path.asserts import \
    assert_expected_confirmed_and_auto_suggestions
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2


@pytest.mark.asyncio
async def test_agency_identification_task(
    db_data_creator: DBDataCreator,
    test_client_session: ClientSession,
    operator: AgencyIdentificationTaskOperator
):
    """Test full flow of AgencyIdentificationTaskOperator"""


    # Confirm does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    collector_type_to_url_id: dict[CollectorType | None, int] = {}

    # Create six urls, one from each strategy
    for strategy in [
        CollectorType.COMMON_CRAWLER,
        CollectorType.AUTO_GOOGLER,
        CollectorType.MUCKROCK_COUNTY_SEARCH,
        CollectorType.MUCKROCK_SIMPLE_SEARCH,
        CollectorType.MUCKROCK_ALL_SEARCH,
        CollectorType.CKAN,
    ]:
        # Create two URLs for each, one pending and one errored
        creation_info: BatchURLCreationInfoV2 = await db_data_creator.batch_v2(
            parameters=TestBatchCreationParameters(
                strategy=strategy,
                urls=[
                    TestURLCreationParameters(
                        count=1,
                        status=URLStatus.PENDING,
                        with_html_content=True
                    ),
                    TestURLCreationParameters(
                        count=1,
                        status=URLStatus.ERROR,
                        with_html_content=True
                    )
                ]
            )
        )
        collector_type_to_url_id[strategy] = creation_info.urls_by_status[URLStatus.PENDING].url_mappings[0].url_id



    # Confirm meets prerequisites
    assert await operator.meets_task_prerequisites()
    # Run task
    run_info = await operator.run_task(1)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message

    # Confirm tasks are piped into the correct subtasks
        # * common_crawler into common_crawler_subtask
        # * auto_googler into auto_googler_subtask
        # * muckrock_county_search into muckrock_subtask
        # * muckrock_simple_search into muckrock_subtask
        # * muckrock_all_search into muckrock_subtask
        # * ckan into ckan_subtask


    mock_run_subtask: AsyncMock = operator.run_subtask

    assert mock_run_subtask.call_count == 7

    #
    #     # Confirm subtask classes are correct for the given urls
    #     d2 = {}
    #     for call_arg in mock_run_subtask.call_args_list:
    #         subtask_class = call_arg[0][0].__class__
    #         url_id = call_arg[0][1]
    #         d2[url_id] = subtask_class
    #
    #
    #     subtask_class_collector_type = [
    #         (MuckrockAgencyIdentificationSubtask, CollectorType.MUCKROCK_ALL_SEARCH),
    #         (MuckrockAgencyIdentificationSubtask, CollectorType.MUCKROCK_COUNTY_SEARCH),
    #         (MuckrockAgencyIdentificationSubtask, CollectorType.MUCKROCK_SIMPLE_SEARCH),
    #         (CKANAgencyIdentificationSubtask, CollectorType.CKAN),
    #         (CommonCrawlerAgencyIdentificationSubtask, CollectorType.COMMON_CRAWLER),
    #         (AutoGooglerAgencyIdentificationSubtask, CollectorType.AUTO_GOOGLER),
    #         (NoCollectorAgencyIdentificationSubtask, None)
    #     ]
    #
    #     for subtask_class, collector_type in subtask_class_collector_type:
    #         url_id = collector_type_to_url_id[collector_type]
    #         assert d2[url_id] == subtask_class
    #
    #
    #     # Confirm task again does not meet prerequisites
    #     assert not await operator.meets_task_prerequisites()
    #
    #
    #
    #
    # #  Check confirmed and auto suggestions
    # adb_client = db_data_creator.adb_client
    # await assert_expected_confirmed_and_auto_suggestions(adb_client)
    #
    #
