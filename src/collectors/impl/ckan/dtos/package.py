from dataclasses import dataclass, field


@dataclass
class Package:
    """
    A class representing a CKAN package (dataset).
    """
    base_url: str = ""
    url: str = ""
    title: str = ""
    agency_name: str = ""
    description: str = ""
    supplying_entity: str = ""
    record_format: list = field(default_factory=lambda: [])
    data_portal_type: str = ""
    source_last_updated: str = ""

    def to_dict(self):
        """
        Returns a dictionary representation of the package.
        """
        return {
            "source_url": self.url,
            "submitted_name": self.title,
            "agency_name": self.agency_name,
            "description": self.description,
            "supplying_entity": self.supplying_entity,
            "record_format": self.record_format,
            "data_portal_type": self.data_portal_type,
            "source_last_updated": self.source_last_updated,
        }
