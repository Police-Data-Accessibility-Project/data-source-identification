from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class FlagURLCheckedForInternetArchives(
    URLDependentMixin,
    Base
):

    success: Mapped[bool]

    __tablename__ = 'flag_url_checked_for_internet_archive'
    __table_args__ = (
        PrimaryKeyConstraint(
            'url_id',
        ),
    )
