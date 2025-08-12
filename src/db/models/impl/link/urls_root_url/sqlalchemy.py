from src.db.models.helpers import url_id_column
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class LinkURLRootURL(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    WithIDBase
):
    __tablename__ = "link_urls_root_url"

    root_url_id = url_id_column()