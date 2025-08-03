from pydantic import BaseModel, model_validator


class URLProbeResponse(BaseModel):
    url: str
    status_code: int | None
    content_type: str | None
    error: str | None = None

    @model_validator(mode='after')
    def check_error_mutually_exclusive_with_content(self):
        if self.error is None:
            if self.content_type is None:
                raise ValueError('Content type required if no error')
            if self.status_code is None:
                raise ValueError('Status code required if no error')
            return self

        if self.content_type is not None:
            raise ValueError('Content type mutually exclusive with error')

        return self
