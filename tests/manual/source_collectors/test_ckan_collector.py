from unittest.mock import MagicMock

from marshmallow import Schema, fields

from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from source_collectors.ckan.CKANCollector import CKANCollector
from source_collectors.ckan.DTOs import CKANInputDTO
from source_collectors.ckan.search_terms import package_search, group_search, organization_search

class CKANSchema(Schema):
    submitted_name = fields.String()
    agency_name = fields.String()
    description = fields.String()
    supplying_entity = fields.String()
    record_format = fields.List(fields.String)
    data_portal_type = fields.String()
    source_last_updated = fields.String()


def test_ckan_collector():
    collector = CKANCollector(
        batch_id=1,
        dto=CKANInputDTO(
            **{
                "package_search": package_search,
                "group_search": group_search,
                "organization_search": organization_search
            }
        ),
        logger=MagicMock(spec=CoreLogger),
        db_client=MagicMock(spec=DatabaseClient),
        raise_error=True

    )
    collector.run()
    schema = CKANSchema(many=True)
    schema.load(collector.data["results"])
