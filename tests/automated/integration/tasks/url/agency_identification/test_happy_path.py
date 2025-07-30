from copy import deepcopy
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from aiohttp import ClientSession
from pdap_access_manager import AccessManager

from src.collectors.enums import CollectorType, URLStatus
from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.enums import SuggestionType
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
from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.external.pdap.client import PDAPClient
from tests.automated.integration.tasks.url.agency_identification.data import SAMPLE_AGENCY_SUGGESTIONS
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2


@pytest.mark.asyncio
async def test_agency_identification_task(db_data_creator: DBDataCreator):
    """Test full flow of AgencyIdentificationTaskOperator"""

    async def mock_run_subtask(
            subtask,
            url_id: int,
            collector_metadata: Optional[dict]
    ):
        # Deepcopy to prevent using the same instance in memory
        suggestion = deepcopy(SAMPLE_AGENCY_SUGGESTIONS[url_id % 3])
        suggestion.url_id = url_id
        suggestion.pdap_agency_id = (url_id % 3) if suggestion.suggestion_type != SuggestionType.UNKNOWN else None
        return [suggestion]

    async with ClientSession() as session:
        mock = MagicMock()
        access_manager = AccessManager(
            email=mock.email,
            password=mock.password,
            api_key=mock.api_key,
            session=session
        )
        pdap_client = PDAPClient(
            access_manager=access_manager
        )
        muckrock_api_interface = MuckrockAPIInterface(session=session)
        with patch.object(
            AgencyIdentificationTaskOperator,
            "run_subtask",
            side_effect=mock_run_subtask,
        ) as mock:
            operator = AgencyIdentificationTaskOperator(
                adb_client=db_data_creator.adb_client,
                pdap_client=pdap_client,
                muckrock_api_interface=muckrock_api_interface
            )

            # Confirm does not yet meet prerequisites
            assert not await operator.meets_task_prerequisites()


            d = {}

            # Create six urls, one from each strategy
            for strategy in [
                CollectorType.COMMON_CRAWLER,
                CollectorType.AUTO_GOOGLER,
                CollectorType.MUCKROCK_COUNTY_SEARCH,
                CollectorType.MUCKROCK_SIMPLE_SEARCH,
                CollectorType.MUCKROCK_ALL_SEARCH,
                CollectorType.CKAN,
                None
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
                d[strategy] = creation_info.urls_by_status[URLStatus.PENDING].url_mappings[0].url_id



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

            assert mock.call_count == 7


            # Confirm subtask classes are correct for the given urls
            d2 = {}
            for call_arg in mock.call_args_list:
                subtask_class = call_arg[0][0].__class__
                url_id = call_arg[0][1]
                d2[url_id] = subtask_class


            subtask_class_collector_type = [
                (MuckrockAgencyIdentificationSubtask, CollectorType.MUCKROCK_ALL_SEARCH),
                (MuckrockAgencyIdentificationSubtask, CollectorType.MUCKROCK_COUNTY_SEARCH),
                (MuckrockAgencyIdentificationSubtask, CollectorType.MUCKROCK_SIMPLE_SEARCH),
                (CKANAgencyIdentificationSubtask, CollectorType.CKAN),
                (CommonCrawlerAgencyIdentificationSubtask, CollectorType.COMMON_CRAWLER),
                (AutoGooglerAgencyIdentificationSubtask, CollectorType.AUTO_GOOGLER),
                (NoCollectorAgencyIdentificationSubtask, None)
            ]

            for subtask_class, collector_type in subtask_class_collector_type:
                url_id = d[collector_type]
                assert d2[url_id] == subtask_class


            # Confirm task again does not meet prerequisites
            assert not await operator.meets_task_prerequisites()




    #  Check confirmed and auto suggestions
    adb_client = db_data_creator.adb_client
    confirmed_suggestions = await adb_client.get_urls_with_confirmed_agencies()
    assert len(confirmed_suggestions) == 2

    agencies = await adb_client.get_all(Agency)
    assert len(agencies) == 2

    auto_suggestions = await adb_client.get_all(AutomatedUrlAgencySuggestion)
    assert len(auto_suggestions) == 4

    # Of the auto suggestions, 2 should be unknown
    assert len([s for s in auto_suggestions if s.is_unknown]) == 2

    # Of the auto suggestions, 2 should not be unknown
    assert len([s for s in auto_suggestions if not s.is_unknown]) == 2
