from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class FlagRootURL(
    CreatedAtMixin,
    URLDependentMixin,
    Base
):
    __tablename__ = 'flag_root_url'
    __table_args__ = (
        PrimaryKeyConstraint(
            'url_id',
        ),
    )
