import pytest

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.common_crawler import \
    CommonCrawlerAgencyIdentificationSubtask
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_common_crawler_subtask(db_data_creator: DBDataCreator):
    # Test that common_crawler subtask correctly adds URL to
    # url_agency_suggestions with label 'Unknown'
    subtask = CommonCrawlerAgencyIdentificationSubtask()
    results: list[URLAgencySuggestionInfo] = await subtask.run(url_id=1, collector_metadata={})
    assert len(results) == 1
    assert results[0].url_id == 1
    assert results[0].suggestion_type == SuggestionType.UNKNOWN
