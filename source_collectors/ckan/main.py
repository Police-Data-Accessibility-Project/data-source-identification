from source_collectors.ckan.ckan_scraper_toolkit import ckan_package_search, ckan_group_package_show, \
    ckan_package_search_from_organization
from source_collectors.ckan.scrape_ckan_data_portals import perform_search, get_flat_list, deduplicate_entries, \
    get_collection_child_packages, filter_result, parse_result, write_to_csv
from source_collectors.ckan.search_terms import package_search, group_search, organization_search



async def main():
    """
    Main function.
    """
    results = []

    print("Gathering results...")
    results = await perform_search(
        search_func=ckan_package_search,
        search_terms=package_search,
        results=results,
    )
    results = await perform_search(
        search_func=ckan_group_package_show,
        search_terms=group_search,
        results=results,
    )
    results = await perform_search(
        search_func=ckan_package_search_from_organization,
        search_terms=organization_search,
        results=results,
    )

    flat_list = get_flat_list(results)
    # Deduplicate entries
    flat_list = deduplicate_entries(flat_list)
    print("\nRetrieving collections...")
    flat_list = get_collection_child_packages(flat_list)

    filtered_results = list(filter(filter_result, flat_list))
    parsed_results = list(map(parse_result, filtered_results))

    write_to_csv(parsed_results)

if __name__ == "__main__":
    main()
