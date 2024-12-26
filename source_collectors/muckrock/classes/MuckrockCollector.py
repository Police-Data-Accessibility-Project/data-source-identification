import itertools

from psycopg.generators import fetch

from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from source_collectors.muckrock.classes.FOIASearcher import FOIASearcher, SearchCompleteException
from source_collectors.muckrock.classes.muckrock_fetchers.FOIAFetcher import FOIAFetcher
from source_collectors.muckrock.classes.muckrock_fetchers.FOIALoopFetcher import FOIALoopFetcher
from source_collectors.muckrock.classes.fetch_requests.FOIALoopFetchRequest import FOIALoopFetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers.JurisdictionGeneratorFetcher import \
    JurisdictionGeneratorFetcher
from source_collectors.muckrock.classes.muckrock_fetchers.JurisdictionLoopFetcher import JurisdictionLoopFetcher
from source_collectors.muckrock.classes.fetch_requests.JurisdictionLoopFetchRequest import JurisdictionLoopFetchRequest
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockFetcher import MuckrockNoMoreDataError
from source_collectors.muckrock.schemas import SimpleSearchCollectorConfigSchema, MuckrockCollectorOutputSchema, \
    MuckrockCountyLevelCollectorConfigSchema, MuckrockAllFOIARequestsCollectorConfigSchema


class MuckrockSimpleSearchCollector(CollectorBase):
    """
    Performs searches on MuckRock's database
    by matching a search string to title of request
    """
    config_schema = SimpleSearchCollectorConfigSchema
    output_schema = MuckrockCollectorOutputSchema
    collector_type = CollectorType.MUCKROCK_SIMPLE_SEARCH

    def check_for_count_break(self, count, max_count) -> None:
        if max_count is None:
            return
        if count >= max_count:
            raise SearchCompleteException

    def run_implementation(self) -> None:
        fetcher = FOIAFetcher()
        searcher = FOIASearcher(
            fetcher=fetcher,
            search_term=self.config["search_string"]
        )
        max_count = self.config["max_results"]
        all_results = []
        results_count = 0
        for search_count in itertools.count():
            try:
                results = searcher.get_next_page_results()
                all_results.extend(results)
                results_count += len(results)
                self.check_for_count_break(results_count, max_count)
            except SearchCompleteException:
                break
            self.log(f"Search {search_count}: Found {len(results)} results")

        self.log(f"Search Complete. Total results: {results_count}")
        self.data = {"urls": self.format_results(all_results)}

    def format_results(self, results: list[dict]) -> list[dict]:
        formatted_results = []
        for result in results:
            formatted_result = {
                "url": result["absolute_url"],
                "metadata": result
            }
            formatted_results.append(formatted_result)

        return formatted_results


class MuckrockCountyLevelSearchCollector(CollectorBase):
    """
    Searches for any and all requests in a certain county
    """
    config_schema = MuckrockCountyLevelCollectorConfigSchema
    output_schema = MuckrockCollectorOutputSchema
    collector_type = CollectorType.MUCKROCK_COUNTY_SEARCH

    def run_implementation(self) -> None:
        jurisdiction_ids = self.get_jurisdiction_ids()
        if jurisdiction_ids is None:
            self.log("No jurisdictions found")
            return
        all_data = self.get_foia_records(jurisdiction_ids)
        formatted_data = self.format_data(all_data)
        self.data = {"urls": formatted_data}

    def format_data(self, all_data):
        formatted_data = []
        for data in all_data:
            formatted_data.append({
                "url": data["absolute_url"],
                "metadata": data
            })
        return formatted_data

    def get_foia_records(self, jurisdiction_ids):
        all_data = []
        for name, id_ in jurisdiction_ids.items():
            self.log(f"Fetching records for {name}...")
            request = FOIALoopFetchRequest(jurisdiction=id_)
            fetcher = FOIALoopFetcher(request)
            fetcher.loop_fetch()
            all_data.extend(fetcher.ffm.results)
        return all_data

    def get_jurisdiction_ids(self):
        parent_jurisdiction_id = self.config["parent_jurisdiction_id"]
        request = JurisdictionLoopFetchRequest(
            level="l",
            parent=parent_jurisdiction_id,
            town_names=self.config["town_names"]
        )
        fetcher = JurisdictionGeneratorFetcher(initial_request=request)
        for message in fetcher.generator_fetch():
            self.log(message)
        jurisdiction_ids = fetcher.jfm.jurisdictions
        return jurisdiction_ids


class MuckrockAllFOIARequestsCollector(CollectorBase):
    """
    Retrieves urls associated with all Muckrock FOIA requests
    """
    config_schema = MuckrockAllFOIARequestsCollectorConfigSchema
    output_schema = MuckrockCollectorOutputSchema
    collector_type = CollectorType.MUCKROCK_ALL_SEARCH

    def run_implementation(self) -> None:
        start_page = self.config["start_page"]
        fetcher = FOIAFetcher(
            start_page=start_page,
        )
        total_pages = self.config["pages"]
        all_page_data = self.get_page_data(fetcher, start_page, total_pages)
        all_transformed_data = self.transform_data(all_page_data)
        self.data = {"urls": all_transformed_data}


    def get_page_data(self, fetcher, start_page, total_pages):
        all_page_data = []
        for page in range(start_page, start_page + total_pages):
            self.log(f"Fetching page {fetcher.current_page}")
            try:
                page_data = fetcher.fetch_next_page()
            except MuckrockNoMoreDataError:
                self.log(f"No more data to fetch at page {fetcher.current_page}")
                break
            if page_data is None:
                continue
            all_page_data.append(page_data)
        return all_page_data

    def transform_data(self, all_page_data):
        all_transformed_data = []
        for page_data in all_page_data:
            for data in page_data["results"]:
                all_transformed_data.append({
                    "url": data["absolute_url"],
                    "metadata": data
                })
        return all_transformed_data