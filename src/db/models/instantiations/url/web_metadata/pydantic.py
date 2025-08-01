from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLWebMetadataPydantic(BulkInsertableModel):
    url_id: int
    accessed: bool
    status_code: int | None
    content_type: str | None
    error_message: str | None