from tests.automated.core.helpers.constants import ALLEGHENY_COUNTY_MUCKROCK_ID, ALLEGHENY_COUNTY_TOWN_NAMES
from collector_manager.enums import CollectorStatus
from source_collectors.muckrock.classes.MuckrockCollector import MuckrockSimpleSearchCollector, \
    MuckrockCountyLevelSearchCollector, MuckrockAllFOIARequestsCollector


def test_muckrock_simple_search_collector():

    collector = MuckrockSimpleSearchCollector(
        name="test_muckrock_simple_search_collector",
        config={
            "search_string": "police",
            "max_results": 10
        }
    )
    collector.run()
    assert collector.status == CollectorStatus.COMPLETED, collector.logs
    assert len(collector.data["urls"]) >= 10

def test_muckrock_county_level_search_collector():
    collector = MuckrockCountyLevelSearchCollector(
        name="test_muckrock_county_level_search_collector",
        config={
            "parent_jurisdiction_id": ALLEGHENY_COUNTY_MUCKROCK_ID,
            "town_names": ALLEGHENY_COUNTY_TOWN_NAMES
        }
    )
    collector.run()
    assert collector.status == CollectorStatus.COMPLETED, collector.logs
    assert len(collector.data["urls"]) >= 10

def test_muckrock_full_search_collector():
    collector = MuckrockAllFOIARequestsCollector(
        name="test_muckrock_full_search_collector",
        config={
            "start_page": 1,
            "pages": 2
        }
    )
    collector.run()
    assert collector.status == CollectorStatus.COMPLETED, collector.logs
    assert len(collector.data["urls"]) >= 1