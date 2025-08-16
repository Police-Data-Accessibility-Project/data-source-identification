from pydantic import BaseModel

from src.external.internet_archives.models.ia_url_mapping import InternetArchivesURLMapping


class IAURLMappingSubsets(BaseModel):
    error: list[InternetArchivesURLMapping] = []
    has_metadata: list[InternetArchivesURLMapping] = []