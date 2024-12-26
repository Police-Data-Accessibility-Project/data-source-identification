from marshmallow import Schema, fields

class MuckrockURLInfoSchema(Schema):
    url = fields.String(required=True)
    metadata = fields.Dict(required=True)

class SimpleSearchCollectorConfigSchema(Schema):
    search_string = fields.String(
        required=True
    )
    max_results = fields.Int(
        load_default=10,
        allow_none=True,
        metadata={"description": "The maximum number of results to return."
                                 "If none, all results will be returned (and may take considerably longer to process)."}
    )

class MuckrockCollectorOutputSchema(Schema):
    urls = fields.List(
        fields.Nested(MuckrockURLInfoSchema),
        required=True
    )

class MuckrockCountyLevelCollectorConfigSchema(Schema):
    parent_jurisdiction_id = fields.Int(required=True)
    town_names = fields.List(
        fields.String(required=True),
        required=True
    )

class MuckrockAllFOIARequestsCollectorConfigSchema(Schema):
    start_page = fields.Int(required=True)
    pages = fields.Int(load_default=1)

