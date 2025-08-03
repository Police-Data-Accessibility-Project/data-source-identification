from src.db.helpers.session.types import BulkActionType
from src.db.models.templates_.base import Base
from src.db.templates.protocols.sa_correlated.core import SQLAlchemyCorrelatedProtocol
from src.db.templates.protocols.sa_correlated.with_id import SQLAlchemyCorrelatedWithIDProtocol
from src.db.utils.validate import validate_all_models_of_same_type


class BulkActionParser:

    def __init__(
        self,
        models: list[BulkActionType],
    ):
        validate_all_models_of_same_type(models)
        model_class = type(models[0])
        self.models = models
        self.model_class = model_class

    @property
    def id_field(self) -> str:
        if not issubclass(self.model_class, SQLAlchemyCorrelatedWithIDProtocol):
            raise TypeError("Model must implement SQLAlchemyCorrelatedWithID protocol.")

        return self.model_class.id_field()

    @property
    def sa_model(self) -> type[Base]:
        if not issubclass(self.model_class, SQLAlchemyCorrelatedProtocol):
            raise TypeError(f"Model {self.model_class} must implement SQLAlchemyCorrelated protocol.")
        return self.model_class.sa_model()

    def get_non_id_fields(self) -> list[str]:
        return [
            field for field in self.model_class.model_fields.keys()
            if field != self.id_field
        ]

    def get_all_fields(self) -> list[str]:
        return [
            field for field in self.model_class.model_fields.keys()
        ]
