from sqlalchemy import Column, Integer

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class BacklogSnapshot(CreatedAtMixin, WithIDBase):
    __tablename__ = "backlog_snapshot"

    count_pending_total = Column(Integer, nullable=False)
