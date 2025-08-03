from abc import abstractmethod
from typing import Protocol, runtime_checkable

from src.db.models.templates_.base import Base


@runtime_checkable
class SQLAlchemyCorrelatedProtocol(Protocol):


    @classmethod
    @abstractmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        pass
