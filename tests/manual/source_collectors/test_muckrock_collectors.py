from unittest.mock import MagicMock, AsyncMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from core.CoreLogger import CoreLogger
from source_collectors.muckrock.DTOs import MuckrockSimpleSearchCollectorInputDTO, \
    MuckrockCountySearchCollectorInputDTO, MuckrockAllFOIARequestsCollectorInputDTO
from source_collectors.muckrock.classes.MuckrockCollector import MuckrockSimpleSearchCollector, \
    MuckrockCountyLevelSearchCollector, MuckrockAllFOIARequestsCollector
from source_collectors.muckrock.schemas import MuckrockURLInfoSchema
from tests.test_automated.integration.core.helpers.constants import ALLEGHENY_COUNTY_MUCKROCK_ID, \
    ALLEGHENY_COUNTY_TOWN_NAMES


@pytest.mark.asyncio
async def test_muckrock_simple_search_collector():

    collector = MuckrockSimpleSearchCollector(
        batch_id=1,
        dto=MuckrockSimpleSearchCollectorInputDTO(
            search_string="police",
            max_results=10
        ),
        logger=MagicMock(spec=CoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    schema = MuckrockURLInfoSchema(many=True)
    schema.load(collector.data["urls"])
    assert len(collector.data["urls"]) >= 10
    print(collector.data)


@pytest.mark.asyncio
async def test_muckrock_county_level_search_collector():
    collector = MuckrockCountyLevelSearchCollector(
        batch_id=1,
        dto=MuckrockCountySearchCollectorInputDTO(
            parent_jurisdiction_id=ALLEGHENY_COUNTY_MUCKROCK_ID,
            town_names=ALLEGHENY_COUNTY_TOWN_NAMES
        ),
        logger=MagicMock(spec=CoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    schema = MuckrockURLInfoSchema(many=True)
    schema.load(collector.data["urls"])
    assert len(collector.data["urls"]) >= 10
    print(collector.data)



@pytest.mark.asyncio
async def test_muckrock_full_search_collector():
    collector = MuckrockAllFOIARequestsCollector(
        batch_id=1,
        dto=MuckrockAllFOIARequestsCollectorInputDTO(
            start_page=1,
            total_pages=2
        ),
        logger=MagicMock(spec=CoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    assert len(collector.data["urls"]) >= 1
    schema = MuckrockURLInfoSchema(many=True)
    schema.load(collector.data["urls"])
    print(collector.data)