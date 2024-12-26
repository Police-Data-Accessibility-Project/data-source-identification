from pydantic import BaseModel

from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from source_collectors.ckan.ckan_scraper_toolkit import ckan_package_search, ckan_group_package_show, \
    ckan_package_search_from_organization
from source_collectors.ckan.schemas import CKANSearchSchema, CKANOutputSchema
from source_collectors.ckan.scrape_ckan_data_portals import perform_search, get_flat_list, deduplicate_entries, \
    get_collections, filter_result, parse_result

SEARCH_FUNCTION_MAPPINGS = {
    "package_search": ckan_package_search,
    "group_search": ckan_group_package_show,
    "organization_search": ckan_package_search_from_organization
}

class CKANCollector(CollectorBase):
    config_schema = CKANSearchSchema
    output_schema = CKANOutputSchema
    collector_type = CollectorType.CKAN

    def run_implementation(self):
        results = []
        for search in SEARCH_FUNCTION_MAPPINGS.keys():
            self.log(f"Running search '{search}'...")
            config = self.config.get(search, None)
            if config is None:
                continue
            func = SEARCH_FUNCTION_MAPPINGS[search]
            results = perform_search(
                search_func=func,
                search_terms=config,
                results=results
            )
        flat_list = get_flat_list(results)
        deduped_flat_list = deduplicate_entries(flat_list)

        new_list = []

        count = len(deduped_flat_list)
        for idx, result in enumerate(deduped_flat_list):
            if "extras" in result.keys():
                self.log(f"Found collection ({idx + 1}/{count}): {result['id']}")
                collections = get_collections(result)
                if collections:
                    new_list += collections[0]
                    continue

            new_list.append(result)

        filtered_results = list(filter(filter_result, flat_list))
        parsed_results = list(map(parse_result, filtered_results))

        self.data = {"results": parsed_results}

