"""
This class combines data with pre-annotation data, converting it into the requisite format for Label Studio
"""
from typing import Any

class BaseResultInfo:
    """
    Contains information required for every result
    """
    def __init__(self, result_type: str, to_name: str, from_name: str, origin: str = "manual"):
        """

        Args:
            result_type: One of the permitted Label Studio result types
            to_name: Name of the entity being labeled
            from_name: Source name of the result in the label configuration
            origin: Where the result came from, defaults to "manual"
        """
        self.result_type = result_type
        self.to_name = to_name
        self.from_name = from_name
        self.origin = origin

class TaxonomyResult:

    def __init__(self, base_info: BaseResultInfo, taxonomy_data: list[list[str]]):
        self.base_info = base_info
        self.taxonomy_data = taxonomy_data

    def to_dict(self) -> dict:
        """
        Converts the taxonomy data to a dictionary
        Returns:

        """
        return {
            "type": self.base_info.result_type,
            "value": {
                "taxonomy": self.taxonomy_data
            },
            "origin": self.base_info.origin,
            "to_name": self.base_info.to_name,
            "from_name": self.base_info.from_name
        }




class PreAnnotationCreator:

    def __init__(self):
        pass

    def add_taxonomy_data(self, raw_taxonomy_data: Any) -> list[list[str]]:
        """
        This method adds taxonomy data to the pre-annotation data

        Taxonomy data exists as a list of lists
            Each sub-list represents a single selection in the taxonomy
            and is a list of strings representing each level of the taxonomy
            with the first being the most superordinate, and the last being the most subordinate
            Selections do not have to include all levels of the taxonomy
            For example, in a taxonomy of animals, if "Dog" is selected, the selection is represented as ["Dog"]
            However, a selection of a subordinate category entails selection of all relevant superordinate categories
            For example, If "German Shepherd" is selected, the selection is represented as ["Dog", "German Shepherd"]
            If "Dog" is also selected, that is included as a separate sub-list containing only ["Dog"]

        Example format:
            [
                ["Dog", "German Shepherd"],
                ["Dog"]
            ]

        Args:
            raw_taxonomy_data: Any: Taxonomy data to be converted into the requisite format for Label Studio
        Returns:
            list[list[str]]: The pre-annotation data with the taxonomy data added

        """

        taxonomy_results = []




        # Note that for multi-hierarchical taxonomy data,
        # any selection of the subordinate category
        # will automatically entail selection of the superordinate category
