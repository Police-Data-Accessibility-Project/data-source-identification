import pytest

from src.db.constants import PLACEHOLDER_AGENCY_NAME
from src.db.models.impl.agency.sqlalchemy import Agency
from tests.helpers.setup.annotate_agency.core import setup_for_annotate_agency
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_annotate_url_agency_agency_not_in_db(db_data_creator: DBDataCreator):
    setup_info = await setup_for_annotate_agency(
        db_data_creator,
        url_count=1
    )

    url_id = setup_info.url_ids[0]
    await db_data_creator.adb_client.add_agency_manual_suggestion(
        agency_id=1,
        url_id=url_id,
        user_id=1,
        is_new=False
    )

    agencies = await db_data_creator.adb_client.get_all(Agency)
    assert len(agencies)
    assert agencies[0].name == PLACEHOLDER_AGENCY_NAME
