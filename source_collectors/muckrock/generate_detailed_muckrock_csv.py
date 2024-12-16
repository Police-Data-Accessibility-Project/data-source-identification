"""
Converts JSON file of MuckRock FOIA requests to CSV for further processing
"""

# TODO: Look into linking up this logic with other components in pipeline.

import argparse
import csv
import time
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from source_collectors.muckrock.muckrock_fetchers.AgencyFetcher import AgencyFetcher
from source_collectors.muckrock.muckrock_fetchers.JurisdictionFetcher import JurisdictionFetcher
from utils import format_filename_json_to_csv, load_json_file


class JurisdictionType(Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    LOCAL = "local"


class AgencyInfo(BaseModel):
    name: Optional[str] = ""
    agency_described: Optional[str] = ""
    record_type: Optional[str] = ""
    description: Optional[str] = ""
    source_url: Optional[str] = ""
    readme_url: Optional[str] = ""
    scraper_url: Optional[str] = ""
    state: Optional[str] = ""
    county: Optional[str] = ""
    municipality: Optional[str] = ""
    agency_type: Optional[str] = ""
    jurisdiction_type: Optional[JurisdictionType] = None
    agency_aggregation: Optional[str] = ""
    agency_supplied: Optional[bool] = False
    supplying_entity: Optional[str] = "MuckRock"
    agency_originated: Optional[bool] = True
    originating_agency: Optional[str] = ""
    coverage_start: Optional[str] = ""
    source_last_updated: Optional[str] = ""
    coverage_end: Optional[str] = ""
    number_of_records_available: Optional[str] = ""
    size: Optional[str] = ""
    access_type: Optional[str] = ""
    data_portal_type: Optional[str] = "MuckRock"
    access_notes: Optional[str] = ""
    record_format: Optional[str] = ""
    update_frequency: Optional[str] = ""
    update_method: Optional[str] = ""
    retention_schedule: Optional[str] = ""
    detail_level: Optional[str] = ""


    def model_dump(self, *args, **kwargs):
        original_dict = super().model_dump(*args, **kwargs)
        original_dict['View Archive'] = ''
        return {key: (value.value if isinstance(value, Enum) else value)
                for key, value in original_dict.items()}

    def keys(self) -> list[str]:
        return list(self.model_dump().keys())


def main():
    json_filename = get_json_filename()
    json_data = load_json_file(json_filename)
    output_csv = format_filename_json_to_csv(json_filename)
    agency_infos = get_agency_infos(json_data)
    write_to_csv(agency_infos, output_csv)


def get_agency_infos(json_data):
    a_fetcher = AgencyFetcher()
    j_fetcher = JurisdictionFetcher()
    agency_infos = []
    # Iterate through the JSON data
    for item in json_data:
        print(f"Writing data for {item.get('title')}")
        agency_data = a_fetcher.get_agency(agency_id=item.get("agency"))
        time.sleep(1)
        jurisdiction_data = j_fetcher.get_jurisdiction(
            jurisdiction_id=agency_data.get("jurisdiction")
        )
        agency_name = agency_data.get("name", "")
        agency_info = AgencyInfo(
            name=item.get("title", ""),
            originating_agency=agency_name,
            agency_described=agency_name
        )
        jurisdiction_level = jurisdiction_data.get("level")
        add_locational_info(agency_info, j_fetcher, jurisdiction_data, jurisdiction_level)
        optionally_add_agency_type(agency_data, agency_info)
        optionally_add_access_info(agency_info, item)

        # Extract the relevant fields from the JSON object
        # TODO: I question the utility of creating columns that are then left blank until later
        #   and possibly in a different file entirely.
        agency_infos.append(agency_info)
    return agency_infos


def write_to_csv(agency_infos, output_csv):
    # Open a CSV file for writing
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=AgencyInfo().keys())

        # Write the header row
        writer.writeheader()

        for agency_info in agency_infos:
            csv_row = agency_info.model_dump()

            # Write the extracted row to the CSV file
            writer.writerow(csv_row)


def get_json_filename():
    # Load the JSON data
    parser = argparse.ArgumentParser(description="Parse JSON from a file.")
    parser.add_argument(
        "--json_file", type=str, required=True, help="Path to the JSON file"
    )
    args = parser.parse_args()
    json_filename = args.json_file
    return json_filename


def add_locational_info(agency_info, j_fetcher, jurisdiction_data, jurisdiction_level):
    # federal jurisdiction level
    if jurisdiction_level == "f":
        agency_info.jurisdiction_type = JurisdictionType.FEDERAL
    # state jurisdiction level
    if jurisdiction_level == "s":
        agency_info.jurisdiction_type = JurisdictionType.STATE
        agency_info.state = jurisdiction_data.get("name")
    # local jurisdiction level
    if jurisdiction_level == "l":
        parent_juris_data = j_fetcher.get_jurisdiction(
            jurisdiction_id=jurisdiction_data.get("parent")
        )
        agency_info.state = parent_juris_data.get("abbrev")
        if "County" in jurisdiction_data.get("name"):
            agency_info.county = jurisdiction_data.get("name")
            agency_info.jurisdiction_type = JurisdictionType.COUNTY
        else:
            agency_info.municipality = jurisdiction_data.get("name")
            agency_info.jurisdiction_type = JurisdictionType.LOCAL


def optionally_add_access_info(agency_info, item):
    absolute_url = item.get("absolute_url")
    for comm in item["communications"]:
        if comm["files"]:
            agency_info.source_url = absolute_url + "#files"
            agency_info.access_type = "Web page,Download,API"
            break


def optionally_add_agency_type(agency_data, agency_info):
    if "Police" in agency_data.get("types"):
        agency_info.agency_type = "law enforcement/police"


if __name__ == "__main__":
    main()