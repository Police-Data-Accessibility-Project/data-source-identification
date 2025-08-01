from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, UpdatedAtMixin, BatchDependentMixin, URLDependentMixin
from src.db.models.templates import StandardModel


class LinkBatchURL(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    BatchDependentMixin,
    StandardModel
):
    __tablename__ = "link_batch_urls"

    url = relationship('URL')
    batch = relationship('Batch')