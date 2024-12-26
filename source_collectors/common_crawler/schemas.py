from marshmallow import Schema, fields


class CommonCrawlerConfigSchema(Schema):
    common_crawl_id = fields.String(required=True, description="The Common Crawl ID", example="CC-MAIN-2022-10")
    url = fields.String(required=True, description="The URL to query", example="*.gov")
    keyword = fields.String(required=True, description="The keyword to search in the url", example="police")
    start_page = fields.Integer(required=False, description="The page to start from", example=1)
    pages = fields.Integer(required=False, description="The number of pages to search", example=1)

class CommonCrawlerOutputSchema(Schema):
    urls = fields.List(
        fields.String(
            required=True
        ),
        required=True,
        description="The list of URLs found in the search"
    )