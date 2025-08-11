from unittest.mock import MagicMock

import pytest

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.collectors.impl.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.collectors.impl.muckrock.enums import AgencyLookupResponseType
from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock import MuckrockAgencyIdentificationSubtask
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.enums import MatchAgencyResponseStatus
from tests.helpers.data_creator.core import DBDataCreator


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
