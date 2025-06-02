from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP

from src.db.models.helpers import get_created_at_column, CURRENT_TIME_SERVER_DEFAULT


class URLDependentMixin:
    url_id = Column(
        Integer,
        ForeignKey(
            'urls.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )


class TaskDependentMixin:
    task_id = Column(
        Integer,
        ForeignKey(
            'tasks.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )


class BatchDependentMixin:
    batch_id = Column(
        Integer,
        ForeignKey(
            'batches.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )


class AgencyDependentMixin:
    agency_id = Column(
        Integer,
        ForeignKey(
            'agencies.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )


class CreatedAtMixin:
    created_at = get_created_at_column()


class UpdatedAtMixin:
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=CURRENT_TIME_SERVER_DEFAULT,
        onupdate=CURRENT_TIME_SERVER_DEFAULT
    )
