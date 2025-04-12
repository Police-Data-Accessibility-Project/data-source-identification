from unittest.mock import MagicMock

from marshmallow import Schema, fields

from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from source_collectors.common_crawler.CommonCrawlerCollector import CommonCrawlerCollector
from source_collectors.common_crawler.DTOs import CommonCrawlerInputDTO


class CommonCrawlerSchema(Schema):
    urls = fields.List(fields.String())

def test_common_crawler_collector():
    collector = CommonCrawlerCollector(
        batch_id=1,
        dto=CommonCrawlerInputDTO(),
        logger=MagicMock(spec=CoreLogger),
        db_client=MagicMock(spec=DatabaseClient)
    )
    collector.run()
    print(collector.data)
    CommonCrawlerSchema().load(collector.data)
