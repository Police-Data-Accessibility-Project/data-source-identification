from sqlalchemy import Column, Integer

from src.db.models.mixins import CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class StandardBase(
    Base,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
