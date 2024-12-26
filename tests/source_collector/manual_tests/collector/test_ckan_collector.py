from source_collectors.ckan.CKANCollector import CKANCollector
from source_collectors.ckan.schemas import CKANSearchSchema
from source_collectors.ckan.search_terms import package_search, group_search, organization_search


def test_ckan_collector():
    collector = CKANCollector(
        name="test_ckan_collector",
        config={
            "package_search": package_search,
            "group_search": group_search,
            "organization_search": organization_search
        }
    )
    collector.run()
    pass