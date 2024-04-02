"""
A dataclass containing all information relevant for searching for an agency's homepage.
"""
import re
from dataclasses import dataclass
from typing import Union


@dataclass
class AgencyInfo:
    """
    A dataclass containing all information relevant for searching for an agency's homepage.
    """
    agency_name: str
    city: str
    state: str
    county: str
    zip_code: str
    website: Union[str, None]
    agency_type: str
    agency_id: str  # This is the unique identifier for the agency in the database

    def __str__(self):
        return f"{self.agency_name} in {self.city}, {self.state} ({self.agency_type})"

    def get_search_string(self) -> str:
        """
        Constructs the search string to be used in search engines.
        """
        search_string = (f"{self.agency_name} {self.city} {self.state} {self.county} "
                         f"{self.zip_code} {self.agency_type}")
        # Strip brackets, parentheses, and quotes from search strings
        pattern = r'[\[\]\"\'\(\)]'
        return re.sub(pattern, "", search_string)
