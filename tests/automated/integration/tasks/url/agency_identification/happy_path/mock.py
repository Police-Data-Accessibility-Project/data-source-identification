from copy import deepcopy
from typing import Optional

from src.core.enums import SuggestionType
from tests.automated.integration.tasks.url.agency_identification.happy_path.data import SAMPLE_AGENCY_SUGGESTIONS


async def mock_run_subtask(
    subtask,
    url_id: int,
    collector_metadata: Optional[dict]
):
    """A mocked version of run_subtask that returns a single suggestion for each url_id."""

    # Deepcopy to prevent using the same instance in memory
    suggestion = deepcopy(SAMPLE_AGENCY_SUGGESTIONS[url_id % 3])
    suggestion.url_id = url_id
    suggestion.pdap_agency_id = (url_id % 3) if suggestion.suggestion_type != SuggestionType.UNKNOWN else None
    return [suggestion]
