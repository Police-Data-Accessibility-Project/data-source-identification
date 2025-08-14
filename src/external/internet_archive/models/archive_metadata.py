from pydantic import BaseModel


class IAArchiveMetadata(BaseModel):
    archive_url: str
    length: int
    digest: str