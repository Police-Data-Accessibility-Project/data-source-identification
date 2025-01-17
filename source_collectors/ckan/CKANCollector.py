from pydantic import BaseModel

from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from core.preprocessors.CKANPreprocessor import CKANPreprocessor
from source_collectors.ckan.DTOs import CKANInputDTO
from source_collectors.ckan.ckan_scraper_toolkit import ckan_package_search, ckan_group_package_show, \
    ckan_package_search_from_organization
from source_collectors.ckan.scrape_ckan_data_portals import perform_search, get_flat_list, deduplicate_entries, \
    get_collections, filter_result, parse_result
from util.helper_functions import base_model_list_dump

SEARCH_FUNCTION_MAPPINGS = {
    "package_search": ckan_package_search,
    "group_search": ckan_group_package_show,
    "organization_search": ckan_package_search_from_organization
}

class CKANCollector(CollectorBase):
    collector_type = CollectorType.CKAN
    preprocessor = CKANPreprocessor

    def run_implementation(self):
        results = self.get_results()
        flat_list = get_flat_list(results)
        deduped_flat_list = deduplicate_entries(flat_list)

        list_with_collection_child_packages = self.add_collection_child_packages(deduped_flat_list)

        filtered_results = list(filter(filter_result, list_with_collection_child_packages))
        parsed_results = list(map(parse_result, filtered_results))

        self.data = {"results": parsed_results}

    def add_collection_child_packages(self, deduped_flat_list):
        # TODO: Find a way to clearly indicate which parts call from the CKAN API
        list_with_collection_child_packages = []
        count = len(deduped_flat_list)
        for idx, result in enumerate(deduped_flat_list):
            if "extras" in result.keys():
                self.log(f"Found collection ({idx + 1}/{count}): {result['id']}")
                collections = get_collections(result)
                if collections:
                    list_with_collection_child_packages += collections[0]
                    continue

            list_with_collection_child_packages.append(result)
        return list_with_collection_child_packages

    def get_results(self):
        results = []
        dto: CKANInputDTO = self.dto
        for search in SEARCH_FUNCTION_MAPPINGS.keys():
            self.log(f"Running search '{search}'...")
            sub_dtos: list[BaseModel] = getattr(dto, search)
            if sub_dtos is None:
                continue
            func = SEARCH_FUNCTION_MAPPINGS[search]
            results = perform_search(
                search_func=func,
                search_terms=base_model_list_dump(model_list=sub_dtos),
                results=results
            )
        return results

