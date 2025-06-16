from copy import deepcopy
from typing import Optional
from unittest.mock import MagicMock, AsyncMock, patch

import pytest
from aiohttp import ClientSession

from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.collectors.source_collectors.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.collectors.source_collectors.muckrock.enums import AgencyLookupResponseType
from src.core.tasks.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.pdap_api.enums import MatchAgencyResponseStatus
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from src.db.models.instantiations.agency import Agency
from src.collectors.enums import CollectorType, URLStatus
from src.core.tasks.enums import TaskOperatorOutcome
from src.core.tasks.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.subtasks.agency_identification.auto_googler import AutoGooglerAgencyIdentificationSubtask
from src.core.tasks.subtasks.agency_identification.ckan import CKANAgencyIdentificationSubtask
from src.core.tasks.subtasks.agency_identification.common_crawler import CommonCrawlerAgencyIdentificationSubtask
from src.core.tasks.subtasks.agency_identification.muckrock import MuckrockAgencyIdentificationSubtask
from src.core.enums import SuggestionType
from pdap_access_manager import AccessManager
from src.pdap_api.dtos.match_agency.response import MatchAgencyResponse
from src.pdap_api.dtos.match_agency.post import MatchAgencyInfo
from src.pdap_api.client import PDAPClient
from tests.helpers.db_data_creator import DBDataCreator, BatchURLCreationInfoV2

sample_agency_suggestions = [
    URLAgencySuggestionInfo(
        url_id=-1, # This will be overwritten
        suggestion_type=SuggestionType.UNKNOWN,
        pdap_agency_id=None,
        agency_name=None,
        state=None,
        county=None,
        locality=None
    ),
    URLAgencySuggestionInfo(
        url_id=-1, # This will be overwritten
        suggestion_type=SuggestionType.CONFIRMED,
        pdap_agency_id=-1,
        agency_name="Test Agency",
        state="Test State",
        county="Test County",
        locality="Test Locality"
    ),
    URLAgencySuggestionInfo(
        url_id=-1, # This will be overwritten
        suggestion_type=SuggestionType.AUTO_SUGGESTION,
        pdap_agency_id=-1,
        agency_name="Test Agency 2",
        state="Test State 2",
        county="Test County 2",
        locality="Test Locality 2"
    )
]

@pytest.mark.asyncio
async def test_agency_preannotation_task(db_data_creator: DBDataCreator):
    async def mock_run_subtask(
            subtask,
            url_id: int,
            collector_metadata: Optional[dict]
    ):
        # Deepcopy to prevent using the same instance in memory
        suggestion = deepcopy(sample_agency_suggestions[url_id % 3])
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
                CollectorType.CKAN
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
                d[strategy] = creation_info.url_creation_infos[URLStatus.PENDING].url_mappings[0].url_id


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

            assert mock.call_count == 6


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
                (AutoGooglerAgencyIdentificationSubtask, CollectorType.AUTO_GOOGLER)
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

@pytest.mark.asyncio
async def test_common_crawler_subtask(db_data_creator: DBDataCreator):
    # Test that common_crawler subtask correctly adds URL to
    # url_agency_suggestions with label 'Unknown'
    subtask = CommonCrawlerAgencyIdentificationSubtask()
    results: list[URLAgencySuggestionInfo] = await subtask.run(url_id=1, collector_metadata={})
    assert len(results) == 1
    assert results[0].url_id == 1
    assert results[0].suggestion_type == SuggestionType.UNKNOWN


@pytest.mark.asyncio
async def test_auto_googler_subtask(db_data_creator: DBDataCreator):
    # Test that auto_googler subtask correctly adds URL to
    # url_agency_suggestions with label 'Unknown'
    subtask = AutoGooglerAgencyIdentificationSubtask()
    results: list[URLAgencySuggestionInfo] = await subtask.run(url_id=1, collector_metadata={})
    assert len(results) == 1
    assert results[0].url_id == 1
    assert results[0].suggestion_type == SuggestionType.UNKNOWN

@pytest.mark.asyncio
async def test_muckrock_subtask(db_data_creator: DBDataCreator):
    # Test that muckrock subtask correctly sends agency name to
    # MatchAgenciesInterface and adds received suggestions to
    # url_agency_suggestions

    # Create mock instances for dependency injections
    muckrock_api_interface_mock = MagicMock(spec=MuckrockAPIInterface)
    pdap_client_mock = MagicMock(spec=PDAPClient)

    # Set up mock return values for method calls
    muckrock_api_interface_mock.lookup_agency.return_value = AgencyLookupResponse(
        type=AgencyLookupResponseType.FOUND,
        name="Mock Agency Name",
        error=None
    )

    pdap_client_mock.match_agency.return_value = MatchAgencyResponse(
        status=MatchAgencyResponseStatus.PARTIAL_MATCH,
        matches=[
            MatchAgencyInfo(
                id=1,
                submitted_name="Mock Agency Name",
            ),
            MatchAgencyInfo(
                id=2,
                submitted_name="Another Mock Agency Name",
            )
        ]
    )

    # Create an instance of MuckrockAgencyIdentificationSubtask with mock dependencies
    muckrock_agency_identification_subtask = MuckrockAgencyIdentificationSubtask(
        muckrock_api_interface=muckrock_api_interface_mock,
        pdap_client=pdap_client_mock
    )

    # Run the subtask
    results: list[URLAgencySuggestionInfo] = await muckrock_agency_identification_subtask.run(
        url_id=1,
        collector_metadata={
            "agency": 123
        }
    )

    # Verify the results
    assert len(results) == 2
    assert results[0].url_id == 1
    assert results[0].suggestion_type == SuggestionType.AUTO_SUGGESTION
    assert results[0].pdap_agency_id == 1
    assert results[0].agency_name == "Mock Agency Name"
    assert results[1].url_id == 1
    assert results[1].suggestion_type == SuggestionType.AUTO_SUGGESTION
    assert results[1].pdap_agency_id == 2
    assert results[1].agency_name == "Another Mock Agency Name"

    # Assert methods called as expected
    muckrock_api_interface_mock.lookup_agency.assert_called_once_with(
        muckrock_agency_id=123
    )
    pdap_client_mock.match_agency.assert_called_once_with(
        name="Mock Agency Name"
    )


@pytest.mark.asyncio
async def test_ckan_subtask(db_data_creator: DBDataCreator):
    # Test that ckan subtask correctly sends agency id to
    # CKANAPIInterface, sends resultant agency name to
    # PDAPClient and adds received suggestions to
    # url_agency_suggestions

    pdap_client = AsyncMock()
    pdap_client.match_agency.return_value = MatchAgencyResponse(
        status=MatchAgencyResponseStatus.PARTIAL_MATCH,
        matches=[
            MatchAgencyInfo(
                id=1,
                submitted_name="Mock Agency Name",
            ),
            MatchAgencyInfo(
                id=2,
                submitted_name="Another Mock Agency Name",
            )
        ]
    )  # Assuming MatchAgencyResponse is a class

    # Create an instance of CKANAgencyIdentificationSubtask
    task = CKANAgencyIdentificationSubtask(pdap_client)

    # Call the run method with static values
    collector_metadata = {"agency_name": "Test Agency"}
    url_id = 1

    # Call the run method
    result = await task.run(url_id, collector_metadata)

    # Check the result
    assert len(result) == 2
    assert result[0].url_id == 1
    assert result[0].suggestion_type == SuggestionType.AUTO_SUGGESTION
    assert result[0].pdap_agency_id == 1
    assert result[0].agency_name == "Mock Agency Name"
    assert result[1].url_id == 1
    assert result[1].suggestion_type == SuggestionType.AUTO_SUGGESTION
    assert result[1].pdap_agency_id == 2
    assert result[1].agency_name == "Another Mock Agency Name"

    # Assert methods called as expected
    pdap_client.match_agency.assert_called_once_with(name="Test Agency")

