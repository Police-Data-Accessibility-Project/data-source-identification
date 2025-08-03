
from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from src.db.enums import ChangeLogOperationType
from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class ChangeLog(CreatedAtMixin, WithIDBase):

    __tablename__ = "change_log"

    operation_type = Column(Enum(ChangeLogOperationType, name="operation_type"))
    table_name: Mapped[str]
    affected_id: Mapped[int]
    old_data = Column("old_data", JSONB, nullable=True)
    new_data = Column("new_data", JSONB, nullable=True)
