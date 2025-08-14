from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.standard import StandardBase


class URLInternetArchivesMetadata(
    StandardBase,
    URLDependentMixin
):
    __tablename__ = 'urls_internet_archive_metadata'

    archive_url: Mapped[str]
    digest: Mapped[str]
    length: Mapped[int]