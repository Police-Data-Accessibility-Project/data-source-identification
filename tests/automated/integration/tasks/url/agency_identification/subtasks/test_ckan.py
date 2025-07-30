from unittest.mock import AsyncMock

import pytest

from src.external.pdap.enums import MatchAgencyResponseStatus
from src.core.tasks.url.operators.agency_identification.subtasks.ckan import CKANAgencyIdentificationSubtask
from src.core.enums import SuggestionType
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from tests.helpers.data_creator.core import DBDataCreator


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

