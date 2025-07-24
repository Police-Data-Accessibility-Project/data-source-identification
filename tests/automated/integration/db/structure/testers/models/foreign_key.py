from dataclasses import dataclass


@dataclass
class ForeignKeyTester:
    column_name: str
    valid_id: int
    invalid_id: int
