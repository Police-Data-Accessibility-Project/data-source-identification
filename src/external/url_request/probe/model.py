from pydantic import BaseModel, model_validator


class URLProbeResponse(BaseModel):
    url: str
    status_code: int | None
    content_type: str | None
    error: str | None = None

    @model_validator(mode='after')
    def check_error_mutually_exclusive_with_status_and_content(self):
        if self.error is not None:
            if self.status_code is not None or self.content_type is not None:
                raise ValueError('Error is mutually exclusive with status code and content type')
        return self
