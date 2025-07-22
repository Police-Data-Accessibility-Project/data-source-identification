from sqlalchemy import UniqueConstraint, Column, Text
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, TaskDependentMixin, URLDependentMixin
from src.db.models.templates import StandardModel


class URLErrorInfo(UpdatedAtMixin, TaskDependentMixin, URLDependentMixin, StandardModel):
    __tablename__ = 'url_error_info'
    __table_args__ = (UniqueConstraint(
        "url_id",
        "task_id",
        name="uq_url_id_error"),
    )

    error = Column(Text, nullable=False)

    # Relationships
    url = relationship("URL", back_populates="error_info")
    task = relationship("Task", back_populates="errored_urls")
