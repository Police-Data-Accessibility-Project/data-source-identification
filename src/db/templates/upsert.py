from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.db.models.templates import Base


class UpsertModel(BaseModel, ABC):
    """An abstract base class for encapsulating upsert operations."""

    @property
    def id_field(self) -> str:
        """Defines the field to be used as the primary key."""
        return "id"

    @property
    @abstractmethod
    def sa_model(self) -> type[Base]:
        """Defines the SQLAlchemy model to be upserted."""
        pass