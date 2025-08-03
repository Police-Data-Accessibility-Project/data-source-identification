from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class URLCheckedForDuplicate(CreatedAtMixin, URLDependentMixin, WithIDBase):
    __tablename__ = 'url_checked_for_duplicate'

    # Relationships
    url = relationship("URL", uselist=False, back_populates="checked_for_duplicate")
