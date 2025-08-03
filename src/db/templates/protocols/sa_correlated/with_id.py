from abc import abstractmethod
from typing import Protocol, runtime_checkable

from src.db.models.templates_.base import Base


@runtime_checkable
class SQLAlchemyCorrelatedWithIDProtocol(Protocol):

    @classmethod
    @abstractmethod
    def id_field(cls) -> str:
        """Defines the field to be used as the primary key."""
        return "id"

    @classmethod
    @abstractmethod
    def sa_model(cls) -> type[Base]:
        """Defines the correlated SQLAlchemy model."""
        pass
