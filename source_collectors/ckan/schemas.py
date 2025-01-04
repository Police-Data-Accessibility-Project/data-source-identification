from marshmallow import Schema, fields


class PackageSearchSchema(Schema):
    count = fields.Int(required=True)
    results = fields.List(fields.Str(), required=True) # TODO: What is the structure of this?