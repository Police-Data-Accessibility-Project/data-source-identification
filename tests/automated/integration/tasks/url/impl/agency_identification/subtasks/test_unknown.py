import pytest

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.impl.unknown import UnknownAgencyIdentificationSubtask


@pytest.mark.asyncio
async def test_unknown_agency_identification_subtask():
    # Test that no_collector subtask correctly adds URL to
    # url_agency_suggestions with label 'Unknown'
    subtask = UnknownAgencyIdentificationSubtask()
    results: list[URLAgencySuggestionInfo] = await subtask.run(url_id=1, collector_metadata={})
    assert len(results) == 1
    assert results[0].url_id == 1
    assert results[0].suggestion_type == SuggestionType.UNKNOWN