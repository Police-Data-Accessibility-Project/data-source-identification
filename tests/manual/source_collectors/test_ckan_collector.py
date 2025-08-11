from unittest.mock import AsyncMock

import pytest
from marshmallow import Schema, fields

from src.collectors.impl.ckan.collector import CKANCollector
from src.core.logger import AsyncCoreLogger
from src.collectors.impl.ckan import collector
from src.collectors.impl.ckan.dtos.input import CKANInputDTO


class CKANSchema(Schema):
    submitted_name = fields.String()
    agency_name = fields.String()
    description = fields.String()
    supplying_entity = fields.String()
    record_format = fields.List(fields.String)
    data_portal_type = fields.String()
    source_last_updated = fields.String()

@pytest.mark.asyncio
async def test_ckan_collector_default():
    collector = CKANCollector(
        batch_id=1,
        dto=CKANInputDTO(
            **{
                "package_search": package_search,
                "group_search": group_search,
                "organization_search": organization_search
            }
        ),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    schema = CKANSchema(many=True)
    schema.load(collector.data["results"])
    print("Printing results")
    print(collector.data["results"])

@pytest.mark.asyncio
async def test_ckan_collector_custom():
    """
    Use this to test how CKAN behaves when using
    something other than the default options provided
    """
    collector = CKANCollector(
        batch_id=1,
        dto=CKANInputDTO(
            **{
              "package_search": [
                {
                  "url": "https://catalog.data.gov/",
                  "terms": [
                    "police",
                    "crime",
                    "tags:(court courts court-cases criminal-justice-system law-enforcement law-enforcement-agencies)"
                  ]
                }
              ],
              "group_search": [
                {
                  "url": "https://catalog.data.gov/",
                  "ids": [
                    "3c648d96-0a29-4deb-aa96-150117119a23",
                    "92654c61-3a7d-484f-a146-257c0f6c55aa"
                  ]
                }
              ],
              "organization_search": [
                {
                  "url": "https://data.houstontx.gov/",
                  "ids": [
                    "https://data.houstontx.gov/"
                  ]
                }
              ]
            }
        ),
        logger=AsyncMock(spec=AsyncCoreLogger),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True
    )
    await collector.run()
    schema = CKANSchema(many=True)
    schema.load(collector.data["results"])