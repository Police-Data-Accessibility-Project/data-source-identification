from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, UpdatedAtMixin, BatchDependentMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class LinkBatchURL(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    BatchDependentMixin,
    WithIDBase
):
    __tablename__ = "link_batch_urls"

    url = relationship('URL', overlaps="batch")
    batch = relationship('Batch', overlaps="url")