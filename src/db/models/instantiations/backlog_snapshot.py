from sqlalchemy import Column, Integer

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates import StandardModel


class BacklogSnapshot(CreatedAtMixin, StandardModel):
    __tablename__ = "backlog_snapshot"

    count_pending_total = Column(Integer, nullable=False)
