import csv
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
from enum import Enum

from agency_homepage_searcher.agency_info import AgencyInfo
from agency_homepage_searcher.google_searcher import GoogleSearcher, QuotaExceededError
from util.huggingface_api_manager import HuggingFaceAPIManager
from util.db_manager import DBManager
from util.miscellaneous_functions import get_filename_friendly_timestamp

MAX_SEARCHES = 100  # Maximum searches to perform at a time when searching for results


class SearchResultEnum(Enum):
    """
    This enum corresponds to an enum column in AGENCY_URL_SEARCH_CACHE
    """
    FOUND_RESULTS = "found_results"
    NO_RESULTS_FOUND = "no_results_found"


class USStateReference:

    def __init__(self, database_manager: DBManager):
        rows = database_manager.execute("SELECT state_iso, state_name FROM public.state_names;")
        self.dict = {}
        for row in rows:
            iso = row["state_iso"]
            name = row["state_name"]
            self.dict[iso] = name

    def get_state_name(self, state_iso: str) -> str:
        try:
            return self.dict[state_iso]
        except KeyError:
            raise ValueError(f"Invalide State Isocode: {state_iso}")


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
        AND homepage_url is null
        AND NOT EXISTS (
            SELECT 1 FROM PUBLIC.AGENCY_URL_SEARCH_CACHE
            WHERE PUBLIC.AGENCIES.AIRTABLE_UID = PUBLIC.AGENCY_URL_SEARCH_CACHE.agency_airtable_uid
        )
    ORDER BY COUNT_DATA_SOURCES DESC
    LIMIT 100 -- Limiting to 100 in acknowledgment of the search engine quota
"""

SQL_UPDATE_CACHE = """
    INSERT INTO public.agency_url_search_cache
    (agency_airtable_uid, search_result)
    VALUES (%s, %s)
"""


@dataclass
class PossibleHomepageURL:
    url: str
    snippet: str


@dataclass
class SearchResults:
    agency_id: str
    search_results: List[PossibleHomepageURL]
    search_result_status: SearchResultEnum


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
        self.us_state_reference = USStateReference(database_manager)

    def create_agency_info(self, agency_row: list) -> AgencyInfo:
        """
        Creates an AgencyInfo object using the provided agency data.
        Args:
            agency_row: Data row of the agency from the database.
        Returns:
            An AgencyInfo object.
        """
        try:
            state_name = self.us_state_reference.get_state_name(agency_row[2])
        except KeyError:
            raise ValueError(f"Invalid state ISO code: {agency_row[2]}")
        return AgencyInfo(
            agency_name=agency_row[0],
            city=agency_row[3],
            state=state_name,
            county=agency_row[4],
            zip_code=agency_row[7],
            website=None,
            agency_type=agency_row[1],
            agency_id=agency_row[5]
        )

    def get_agencies_without_homepage_urls(self) -> list[AgencyInfo]:
        """
        Retrieves a list of agencies without homepage URLs.
        Returns: list[AgencyInfo]
        """
        agency_rows = self.database_manager.execute(SQL_GET_AGENCIES_WITHOUT_HOMEPAGE_URLS)
        return [self.create_agency_info(agency_row) for agency_row in agency_rows]

    def search(self, agency_info: AgencyInfo) -> Union[SearchResults, None]:
        """
        Searches for possible homepage URLs for a single agency.
        Args:
            agency_info: information about the agency
        Returns: either the search results or None if the quota is exceeded
        """
        try:
            search_results = self.search_engine.search(
                query=agency_info.get_search_string()
            )
            first_ten_results = self._get_first_ten_results(search_results)
            if len(first_ten_results) > 0:
                search_result_status = SearchResultEnum.FOUND_RESULTS
            else:
                search_result_status = SearchResultEnum.NO_RESULTS_FOUND
            return SearchResults(
                agency_id=agency_info.agency_id,
                search_results=first_ten_results,
                search_result_status=search_result_status
            )
        except QuotaExceededError:
            print("Quota exceeded")
            return None

    @staticmethod
    def _get_first_ten_results(results: list[dict]):
        """
        Extracts first ten results and forms a list of PossibleHomepageURL objects.

        Args:
        - results: A list that fetches from the search engine.

        Returns:
        - List[PossibleHomepageURL]: list containing first ten or less elements.
        """
        if results is None:
            return []
        first_ten_results = []
        for result in results[:10]:
            possible_homepage_url = PossibleHomepageURL(
                url=result['link'],
                snippet=result['snippet'] if 'snippet' in result else ''
            )
            first_ten_results.append(possible_homepage_url)
        return first_ten_results

    def search_until_limit_reached(
            self,
            agency_info_list: list[AgencyInfo],
            max_searches: int = MAX_SEARCHES
    ) -> list[SearchResults]:
        """
        Searches for possible homepage URLs for agencies until the limit is reached.
        Args:
            agency_info_list: list[AgencyInfo] - the list of agencies to search
            max_searches: int - the maximum number of searches to perform
        Returns: list[SearchResults] - the search results
        """
        search_results = []
        for search_count, agency_info in enumerate(agency_info_list):
            if search_count >= max_searches:
                break
            try:
                search_result = self.search(agency_info)
            except Exception as e:
                return self._handle_search_error(e, search_results)
            if search_result is None:  # Quota exceeded
                break
            search_results.append(search_result)
        return search_results

    @staticmethod
    def _handle_search_error(error: Exception, search_results: list[SearchResults]) -> list[SearchResults]:
        """
        Handles search error and returns existing search results.

        Args:
            error (Exception): The error that occurred while searching.
            search_results (list[SearchResults]): The existing search results.
        Returns:
            list[SearchResults]: The existing search results.
        """
        print(f"An error occurred while searching. Error type: {type(error).__name__}, Error message: {error}")
        print("Returning existing search results")
        return search_results

    def write_to_temporary_csv(self, data: List[SearchResults]) -> Path:
        """
        Writes the search results to a temporary CSV file
        which will be uploaded to HuggingFace.

        Args:
            data: List[SearchResults] - the search results
        Returns: Path - the path to the temporary file
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as tmpfile:
            writer = csv.writer(tmpfile, lineterminator='\n')
            # Write the header
            writer.writerow(["agency_id", "url", "snippet"])
            for search_result in data:
                self._write_search_result_to_csv(search_result, writer)
            # Remember the file name for later access
            temp_file_path = Path(tmpfile.name)
        return temp_file_path

    @staticmethod
    def _write_search_result_to_csv(search_result: SearchResults, writer: csv.writer) -> None:
        """
        Args:
            search_result (SearchResults): An object that contains the search results.
            writer (csv.writer): A writer object used to write the search results to a CSV file.

        Raises:
            Exception: If an unexpected error occurs while writing the search results.

        Example:
            search_result = SearchResults()
            writer = csv.writer(...)
            _write_search_result_to_csv(search_result, writer)
        """
        try:
            for possible_homepage_url in search_result.search_results:
                writer.writerow([search_result.agency_id, possible_homepage_url.url, possible_homepage_url.snippet])
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while writing search results for {search_result.agency_id}: {e}")

    def update_search_cache(self, search_results: list[SearchResults]) -> None:
        """
        Updates the search cache for the given agency IDs.
        Args:
            search_results:
        """
        parameters = []
        for search_result in search_results:
            parameter = (search_result.agency_id, search_result.search_result_status.value)
            parameters.append(parameter)
        self.database_manager.executemany(SQL_UPDATE_CACHE, parameters)

    def _try_search_agency_info(self, agency_info: AgencyInfo) -> Union[SearchResults, List]:
        """
        Args:
            agency_info: The agency information to be searched.

        Returns:
            The result of the search operation, or an empty list if an error occurs during the search.
        """
        try:
            return self.search(agency_info)
        except Exception as e:
            return self._handle_search_error(e, [])

    def search_and_upload(self, max_searches: int = MAX_SEARCHES) -> None:
        """
        Searches for possible homepage URLs for agencies without homepage URLs and uploads the results to HuggingFace.
        Args:
            max_searches: the maximum number of searches to perform
        Returns: None
        """
        agency_info_list = self.get_agencies_without_homepage_urls()
        print(f"Searching for homepage URLs for first {max_searches} agencies...")
        search_results = self.search_until_limit_reached(agency_info_list=agency_info_list, max_searches=max_searches)
        print(f"Obtained {len(search_results)} search results")
        self.upload_to_huggingface(search_results)
        self.update_search_cache(search_results)

    def upload_to_huggingface(self, search_results: List[SearchResults]) -> None:
        """
        Uploads search results to HuggingFace.
        Args:
            search_results (List): List of search results to upload.
        Returns:
            None
        """
        temp_file_path = self.write_to_temporary_csv(search_results)
        timestamp = get_filename_friendly_timestamp()
        self.huggingface_api_manager.upload_file(
            local_file_path=temp_file_path,
            repo_file_path=f"/data/search_results_{timestamp}.csv"
        )
        print(f"Uploaded {len(search_results)} search results to HuggingFace: "
              f"huggingface.co/datasets/{self.huggingface_api_manager.repo_id}")
        temp_file_path.unlink()  # Clean up the temporary file
