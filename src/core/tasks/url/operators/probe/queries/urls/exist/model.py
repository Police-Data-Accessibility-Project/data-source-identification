from pydantic import BaseModel


class UrlExistsResult(BaseModel):
    url: str
    url_id: int | None

    @property
    def exists(self):
        return self.url_id is not None