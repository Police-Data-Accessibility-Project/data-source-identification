from unittest.mock import MagicMock, AsyncMock

import pytest
from marshmallow import Schema, fields

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from core.AsyncCoreLogger import AsyncCoreLogger
from source_collectors.common_crawler.CommonCrawlerCollector import CommonCrawlerCollector
from source_collectors.common_crawler.DTOs import CommonCrawlerInputDTO


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
