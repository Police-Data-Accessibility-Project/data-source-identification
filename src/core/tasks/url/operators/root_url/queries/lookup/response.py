from pydantic import BaseModel, model_validator


class LookupRootsURLResponse(BaseModel):
    url: str
    url_id: int | None
    flagged_as_root: bool

    @property
    def exists_in_db(self) -> bool:
        return self.url_id is not None

    @model_validator(mode='after')
    def validate_flagged_as_root(self):
        if self.flagged_as_root and self.url_id is None:
            raise ValueError('URL ID should be provided if flagged as root')
        return self