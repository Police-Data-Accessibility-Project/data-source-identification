from unittest.mock import AsyncMock

import pytest
from marshmallow import Schema, fields

from src.db import AsyncDatabaseClient
from src.core.AsyncCoreLogger import AsyncCoreLogger
from src.source_collectors.common_crawler import CommonCrawlerCollector
from src.source_collectors.common_crawler.DTOs import CommonCrawlerInputDTO


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
