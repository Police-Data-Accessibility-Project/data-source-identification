from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion


async def assert_expected_confirmed_and_auto_suggestions(adb_client: AsyncDatabaseClient):
    confirmed_suggestions = await adb_client.get_urls_with_confirmed_agencies()

    # The number of confirmed suggestions is dependent on how often
    # the subtask iterated through the sample agency suggestions defined in `data.py`
    assert len(confirmed_suggestions) == 3
    agencies = await adb_client.get_all(Agency)
    assert len(agencies) == 2
    auto_suggestions = await adb_client.get_all(AutomatedUrlAgencySuggestion)
    assert len(auto_suggestions) == 4
    # Of the auto suggestions, 2 should be unknown
    assert len([s for s in auto_suggestions if s.is_unknown]) == 2
    # Of the auto suggestions, 2 should not be unknown
    assert len([s for s in auto_suggestions if not s.is_unknown]) == 2
