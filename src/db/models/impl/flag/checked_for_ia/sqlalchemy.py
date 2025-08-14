from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class FlagURLCheckedForInternetArchives(
    WithIDBase,
    URLDependentMixin
):

    __table__ = 'flag_url_checked_for_internet_archive'
    __table_args__ = (
        PrimaryKeyConstraint(
            'url_id',
        ),
    )
