from marshmallow import Schema, fields

class MuckrockURLInfoSchema(Schema):
    url = fields.String(required=True)
    metadata = fields.Dict(required=True)
