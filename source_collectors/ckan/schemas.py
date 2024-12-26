from marshmallow import Schema, fields


class PackageSearchSchema(Schema):
    url = fields.String(required=True)
    terms = fields.List(fields.String(required=True), required=True)

class GroupAndOrganizationSearchSchema(Schema):
    url =  fields.String(required=True)
    ids =  fields.List(fields.String(required=True), required=True)

class CKANSearchSchema(Schema):
    package_search = fields.List(fields.Nested(PackageSearchSchema))
    group_search = fields.List(fields.Nested(GroupAndOrganizationSearchSchema))
    organization_search = fields.List(fields.Nested(GroupAndOrganizationSearchSchema))

class CKANOutputInnerSchema(Schema):
    source_url = fields.String(required=True)
    submitted_name = fields.String(required=True)
    agency_name = fields.String(required=True)
    description = fields.String(required=True)
    supplying_entity = fields.String(required=True)
    record_format = fields.List(fields.String(required=True), required=True)
    data_portal_type = fields.String(required=True)
    source_last_updated = fields.Date(required=True)

class CKANOutputSchema(Schema):
    results = fields.List(fields.Nested(CKANOutputInnerSchema), required=True)