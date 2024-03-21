import csv
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Union

from agency_homepage_searcher.agency_info import AgencyInfo
from agency_homepage_searcher.google_searcher import GoogleSearcher
from agency_homepage_searcher.huggingface_api_manager import HuggingFaceAPIManager
from util.db_manager import DBManager

STATE_ISO_TO_NAME_DICT = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

SQL_GET_AGENCIES_WITHOUT_HOMEPAGE_URLS = """
    SELECT
        SUBMITTED_NAME,
        JURISDICTION_TYPE,
        STATE_ISO,
        MUNICIPALITY,
        COUNTY_NAME,
        AIRTABLE_UID,
        COUNT_DATA_SOURCES,
        ZIP_CODE,
        NO_WEB_PRESENCE -- Relevant
    FROM
        PUBLIC.AGENCIES
    WHERE 
    approved = true
    and homepage_url is null
    ORDER BY COUNT_DATA_SOURCES DESC
    LIMIT 100 -- Limiting to 100 in acknowledgment of the search engine quota
"""


@dataclass
class PossibleHomepageURL:
    url: str
    snippet: str


@dataclass
class SearchResults:
    agency_id: str
    search_results: List[PossibleHomepageURL]


def get_filename_friendly_timestamp() -> str:
    # Get the current datetime
    now = datetime.now()
    # Format the datetime in a filename-friendly format
    # Example: "2024-03-20_15-30-45"
    return now.strftime("%Y-%m-%d_%H-%M-%S")


class HomepageSearcher:
    def __init__(
            self,
            search_engine: GoogleSearcher,
            database_manager: DBManager,
            huggingface_api_manager: HuggingFaceAPIManager
    ):
        self.search_engine = search_engine
        self.database_manager = database_manager
        self.huggingface_api_manager = huggingface_api_manager

    def get_agencies_without_homepage_urls(self) -> list[AgencyInfo]:
        # This is a placeholder for the actual functionality
        agency_rows = self.database_manager.execute(SQL_GET_AGENCIES_WITHOUT_HOMEPAGE_URLS)
        results = []

        for agency_row in agency_rows:
            try:
                state_name = STATE_ISO_TO_NAME_DICT[agency_row[2]]
            except KeyError:
                raise ValueError(f"Invalid state ISO code: {agency_row[2]}")
            agency_info = AgencyInfo(
                agency_name=agency_row[0],
                city=agency_row[3],
                state=state_name,
                county=agency_row[4],
                zip_code=agency_row[7],
                website=None,
                agency_type=agency_row[1],
                agency_id=agency_row[5]
            )
            results.append(agency_info)
        return results

    @staticmethod
    def build_search_string(agency_info: AgencyInfo) -> str:
        """
        Builds the search string which will be used in the search engine search
        Args:
            agency_info:

        Returns:

        """
        search_string = (f"{agency_info.agency_name} {agency_info.city} {agency_info.state} {agency_info.county} "
                         f"{agency_info.zip_code} {agency_info.website} {agency_info.agency_type}")
        return search_string

    def search(self, agency_info: AgencyInfo) -> Union[SearchResults, None]:
        # This is a placeholder for the actual search functionality
        search_string = self.build_search_string(agency_info)
        search_results = self.search_engine.search(search_string)
        if search_results is None:  # Quota exceeded
            return None
        # For now, return the first 10 results
        search_result = SearchResults(
            agency_id=agency_info.agency_id,
            search_results=[PossibleHomepageURL(url=result['link'], snippet=result['snippet']) for result in
                            search_results])
        return search_result

    def search_until_quota_exceeded(
            self,
            agency_info_list: list[AgencyInfo],
            max_searches: int = 100
    ) -> list[SearchResults]:
        # This is a placeholder for the actual search functionality
        search_results = []
        for search_count, agency_info in enumerate(agency_info_list):
            if search_count >= max_searches:
                break
            search_result = self.search(agency_info)
            if search_result is None:  # Quota exceeded
                break
            search_results.append(search_result)
        return search_results

    def write_to_temporary_csv(self, data: List[SearchResults]) -> Path:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmpfile:
            writer = csv.writer(tmpfile)
            # Write the header
            writer.writerow(["agency_id", "url", "snippet"])
            for search_result in data:
                for possible_homepage_url in search_result.search_results:
                    writer.writerow([search_result.agency_id, possible_homepage_url.url, possible_homepage_url.snippet])
            # Remember the file name for later access
            temp_file_path = Path(tmpfile.name)
        return temp_file_path

    def search_and_upload(self, max_searches: int = 100) -> None:
        """
        Searches for possible homepage URLs for agencies without homepage URLs and uploads the results to HuggingFace.
        Args:
            max_searches: the maximum number of searches to perform

        Returns:

        """
        agencies = self.get_agencies_without_homepage_urls()
        search_results = self.search_until_quota_exceeded(
            agency_info_list=agencies,
            max_searches=max_searches
        )
        temp_file_path = self.write_to_temporary_csv(search_results)
        timestamp = get_filename_friendly_timestamp()
        self.huggingface_api_manager.upload_file(
            local_file_path=temp_file_path,
            repo_file_path=f"/data/search_results_{timestamp}.csv"
        )
        temp_file_path.unlink()  # Clean up the temporary file

if __name__ == "__main__":
    # Load the custom search API key and CSE ID from the .env file
    from dotenv import load_dotenv
    load_dotenv()
    google_searcher = GoogleSearcher(
        api_key=os.getenv("CUSTOM_SEARCH_API_KEY"),
        cse_id=os.getenv("CUSTOM_SEARCH_ENGINE_ID"))
    db_manager = DBManager(
        user=os.getenv("DIGITAL_OCEAN_DB_USERNAME"),
        password=os.getenv("DIGITAL_OCEAN_DB_PASSWORD"),
        host=os.getenv("DIGITAL_OCEAN_DB_HOST"),
        port=os.getenv("DIGITAL_OCEAN_DB_PORT"),
        db_name=os.getenv("DIGITAL_OCEAN_DB_NAME")
    )
    huggingface_api_manager = HuggingFaceAPIManager(
        access_token=os.getenv("HUGGINGFACE_ACCESS_TOKEN"),
        repo_id="PDAP/possible_homepage_urls"
    )
    homepage_searcher = HomepageSearcher(
        search_engine=google_searcher,
        database_manager=db_manager,
        huggingface_api_manager=huggingface_api_manager
    )
    homepage_searcher.search_and_upload(
        max_searches=1
    )
