from pydantic import BaseModel


class URLRootURLMapping(BaseModel):
    url: str
    root_url: str

    @property
    def is_root_url(self) -> bool:
        return self.url == self.root_url