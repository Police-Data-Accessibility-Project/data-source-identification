from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates import StandardBase


class URLCheckedForDuplicate(CreatedAtMixin, URLDependentMixin, StandardBase):
    __tablename__ = 'url_checked_for_duplicate'

    # Relationships
    url = relationship("URL", uselist=False, back_populates="checked_for_duplicate")
