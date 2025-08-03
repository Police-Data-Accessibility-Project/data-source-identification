from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, TaskDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class TaskError(UpdatedAtMixin, TaskDependentMixin, WithIDBase):
    __tablename__ = 'task_errors'

    error = Column(Text, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="error")

    __table_args__ = (UniqueConstraint(
        "task_id",
        "error",
        name="uq_task_id_error"),
    )
