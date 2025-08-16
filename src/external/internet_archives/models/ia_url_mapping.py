from pydantic import BaseModel

from src.external.internet_archives.models.archive_metadata import IAArchiveMetadata


class InternetArchivesURLMapping(BaseModel):
    url: str
    ia_metadata: IAArchiveMetadata | None
    error: str | None

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def has_metadata(self) -> bool:
        return self.ia_metadata is not None
