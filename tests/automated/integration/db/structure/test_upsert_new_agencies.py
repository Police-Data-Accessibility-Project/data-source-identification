import pytest

from src.core.enums import SuggestionType
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.db.models.impl.agency.sqlalchemy import Agency
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_upsert_new_agencies(
    wiped_database,
    db_data_creator: DBDataCreator
):
    """
    Check that if the agency doesn't exist, it is added
    But if the agency does exist, it is updated with new information
    """

    suggestions = []
    for i in range(3):
        suggestion = URLAgencySuggestionInfo(
            url_id=1,
            suggestion_type=SuggestionType.AUTO_SUGGESTION,
            pdap_agency_id=i,
            agency_name=f"Test Agency {i}",
            state=f"Test State {i}",
            county=f"Test County {i}",
            locality=f"Test Locality {i}",
            user_id=1
        )
        suggestions.append(suggestion)

    adb_client = db_data_creator.adb_client
    await adb_client.upsert_new_agencies(suggestions)

    update_suggestion = URLAgencySuggestionInfo(
        url_id=1,
        suggestion_type=SuggestionType.AUTO_SUGGESTION,
        pdap_agency_id=0,
        agency_name="Updated Test Agency",
        state="Updated Test State",
        county="Updated Test County",
        locality="Updated Test Locality",
        user_id=1
    )

    await adb_client.upsert_new_agencies([update_suggestion])

    rows = await adb_client.get_all(Agency, order_by_attribute="agency_id")

    assert len(rows) == 3

    d = {}
    for row in rows:
        d[row.agency_id] = row.name

    assert d[0] == "Updated Test Agency"
    assert d[1] == "Test Agency 1"
    assert d[2] == "Test Agency 2"
