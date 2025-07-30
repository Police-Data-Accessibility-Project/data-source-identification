import pytest

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.no_collector import \
    NoCollectorAgencyIdentificationSubtask


@pytest.mark.asyncio
async def test_no_collector_subtask():
    # Test that no_collector subtask correctly adds URL to
    # url_agency_suggestions with label 'Unknown'
    subtask = NoCollectorAgencyIdentificationSubtask()
    results: list[URLAgencySuggestionInfo] = await subtask.run(url_id=1, collector_metadata={})
    assert len(results) == 1
    assert results[0].url_id == 1
    assert results[0].suggestion_type == SuggestionType.UNKNOWN