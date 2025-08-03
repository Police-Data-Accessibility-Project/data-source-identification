from sqlalchemy import Column
from sqlalchemy.orm import relationship

from src.db.enums import PGEnum, TaskType
from src.db.models.mixins import UpdatedAtMixin
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import batch_status_enum


class Task(UpdatedAtMixin, WithIDBase):
    __tablename__ = 'tasks'

    task_type = Column(
        PGEnum(
            *[task_type.value for task_type in TaskType],
            name='task_type'
        ), nullable=False)
    task_status = Column(batch_status_enum, nullable=False)

    # Relationships
    urls = relationship(
        "URL",
        secondary="link_task_urls",
        back_populates="tasks"
    )
    error = relationship("TaskError", back_populates="task")
    errored_urls = relationship("URLErrorInfo", back_populates="task")
