from dataclasses import dataclass

from tests.automated.integration.db.structure.types import SATypes


@dataclass
class ColumnTester:
    column_name: str
    type_: SATypes
    allowed_values: list
