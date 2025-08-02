from pydantic import BaseModel


class URLProbePlannedResponse(BaseModel):
    status_code: int | None
    content_type: str | None
    error: str | None