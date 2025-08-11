from unittest.mock import AsyncMock

import pytest
from marshmallow import Schema, fields

from src.core.logger import AsyncCoreLogger
from src.collectors.impl.common_crawler import collector
from src.collectors.impl.common_crawler import CommonCrawlerInputDTO


class CommonCrawlerSchema(Schema):
    urls = fields.List(fields.String())

@pytest.mark.asyncio
async def test_common_crawler_collector():
    collector = CommonCrawlerCollector(
        batch_id=1,
        dto=CommonCrawlerInputDTO(),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    print(collector.data)
    CommonCrawlerSchema().load(collector.data)
