from dataclasses import dataclass, fields


@dataclass(frozen=True)
class LabelsBase:

    def get_all_labels(self) -> list[str]:
        return [getattr(self, f.name) for f in fields(self)]