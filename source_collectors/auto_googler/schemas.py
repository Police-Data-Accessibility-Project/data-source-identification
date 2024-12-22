from marshmallow import Schema, fields, ValidationError



class AutoGooglerCollectorConfigSchema(Schema):
    api_key = fields.Str(
        required=True,
        allow_none=False,
        metadata={"description": "The API key required for accessing the Google Custom Search API."}
    )
    cse_id = fields.Str(
        required=True,
        allow_none=False,
        metadata={"description": "The CSE (Custom Search Engine) ID required for identifying the specific search engine to use."}
    )
    urls_per_result = fields.Int(
        required=False,
        allow_none=False,
        metadata={"description": "Maximum number of URLs returned per result. Minimum is 1. Default is 10"},
        validate=lambda value: value >= 1,
        load_default=10
    )
    queries = fields.List(
        fields.Str(),
        required=True,
        allow_none=False,
        metadata={"description": "List of queries to search for."},
        validate=lambda value: len(value) > 0
    )

class AutoGooglerCollectorInnerOutputSchema(Schema):
    title = fields.Str(
        metadata={"description": "The title of the result."}
    )
    url = fields.Str(
        metadata={"description": "The URL of the result."}
    )
    snippet = fields.Str(
        metadata={"description": "The snippet of the result."}
    )

class AutoGooglerCollectorResultSchema(Schema):
    query = fields.Str(
        metadata={"description": "The query used for the search."}
    )
    query_results = fields.List(
        fields.Nested(AutoGooglerCollectorInnerOutputSchema),
        metadata={"description": "List of results for each query."}
    )

class AutoGooglerCollectorOuterOutputSchema(Schema):
    data = fields.List(
        fields.Nested(AutoGooglerCollectorResultSchema),
        required=True,
        allow_none=False
    )