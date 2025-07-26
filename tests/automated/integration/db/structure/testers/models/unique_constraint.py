from dataclasses import dataclass


@dataclass
class UniqueConstraintTester:
    columns: list[str]
