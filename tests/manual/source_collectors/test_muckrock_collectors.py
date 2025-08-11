from unittest.mock import AsyncMock

import pytest
from marshmallow import Schema, fields

from src.core.logger import AsyncCoreLogger
from src.collectors.impl.muckrock.collectors.all_foia.dto import MuckrockAllFOIARequestsCollectorInputDTO
from src.collectors.impl.muckrock.collectors.county.dto import MuckrockCountySearchCollectorInputDTO
from src.collectors.impl.muckrock.collectors.simple.dto import MuckrockSimpleSearchCollectorInputDTO
from src.collectors.impl import MuckrockSimpleSearchCollector, \
    MuckrockCountyLevelSearchCollector, MuckrockAllFOIARequestsCollector
from src.db.client.async_ import AsyncDatabaseClient
from tests.automated.integration.core.helpers.constants import ALLEGHENY_COUNTY_MUCKROCK_ID, \
    ALLEGHENY_COUNTY_TOWN_NAMES

class MuckrockURLInfoSchema(Schema):
    url = fields.String(required=True)
    metadata = fields.Dict(required=True)


@pytest.mark.asyncio
async def test_muckrock_simple_search_collector():

    collector = MuckrockSimpleSearchCollector(
        batch_id=1,
        dto=MuckrockSimpleSearchCollectorInputDTO(
            search_string="police",
            max_results=10
        ),
        logger=AsyncMock(spec=AsyncCoreLogger),
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
        logger=AsyncMock(spec=AsyncCoreLogger),
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
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    assert len(collector.data["urls"]) >= 1
    schema = MuckrockURLInfoSchema(many=True)
    schema.load(collector.data["urls"])
    print(collector.data)