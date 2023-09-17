import csv
import os
import re
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from tqdm import tqdm


def get_urls(file=sys.argv[1]):
    """Retrieves a list of urls for identification from file.

    Args:
        file (str, optional): Name of the file to read urls from. Defaults to sys.argv[1].

    Returns:
        list: List of urls to identify.
    """
    with open(file, "r") as f:
        urls = f.readlines()

    if file.endswith(".csv"):
        urls.pop(0)

    return urls


def get_agencies_data():
    """Retrives a list of agency dictionaries from file.

    Returns:
        list: List of agency dictionaries.
    """
    # This is here for when the API is able to return all data from the agencies table
    # For now, the script will use PDAP Criminal Legal Agencies.csv
    # load_dotenv()
    # api_key = "Bearer " + os.getenv("PDAP_API_KEY")

    # response = requests.get("https://data-sources-app-bda3z.ondigitalocean.app/agencies", headers={"Authorization": api_key})
    # if response.status_code != 200:
    #    print("Request to PDAP API failed. Response code:", response.status_code)
    #    exit()
    # response_json = response.json()

    with open("PDAP Criminal Legal Agencies.csv", encoding="utf-8-sig") as agencies:
        agencies_list = list(csv.DictReader(agencies))

    return agencies_list


def parse_hostname(url):
    """Retrieves the hostname (example.com) from a url string.

    Args:
        url (str): Url to parse.

    Returns:
        str: The url's hostname.
    """
    url = url.strip().strip('"')

    if not url.startswith("http"):
        url = "http://" + url

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    hostname = remove_www(hostname)

    return hostname


def remove_http(url):
    """Removes http(s)://www. from a given url so that different protocols don't throw off the matcher.

    Args:
        url (str): Url to remove http from.

    Returns:
        str: The url without http(s)://www.
    """
    url = url.strip().strip('"')

    if not url.startswith("http"):
        url = remove_www(url)
        return url

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    path = parsed_url.path

    hostname = remove_www(hostname)

    url = hostname + path

    if url[-1] != "/":
        url += "/"

    return url


def remove_www(url):
    """Utility function for remove_http() and parse_hostname().

    Removes www. from a url to facilitate better matching for cases where www. is missing.

    Args:
        url (str): Url to remove www. from.

    Returns:
        str: The url without www.
    """
    if url.startswith("www."):
        url = url[4:]

    return url


def match_agencies(agencies, agency_hostnames, url):
    """Attempts to match a url with an agency.

    Args:
        agencies (list): List of agency dictionaries.
        agency_hostnames (list): List of corresponding agency hostnames.
        url (str): Url to match.

    Returns:
        dict: Dictionary of a match in the form {"url": url, "agency": matched_agency}.
    """
    url = url.strip().strip('"')
    url_hostname = parse_hostname(url)

    if url_hostname in agency_hostnames:
        # All agencies with the same hostname as the url are found
        matched_agency = [
            agencies[i] for i, agency_hostname in enumerate(agency_hostnames) if url_hostname == agency_hostname
        ]
    else:
        return {"url": url, "agency": []}

    # More than one agency was found
    if len(matched_agency) > 1:
        url_no_http = remove_http(url)

        for agency in matched_agency:
            agency_homepage = remove_http(agency["homepage_url"])
            # It is assumed that if the url begins with the agency's url, then it belongs to that agency
            if url_no_http.startswith(agency_homepage):
                matched_agency[0] = agency
                break

    return {"url": url, "agency": matched_agency[0]}


def write_csv(matches):
    """Write matches to a CSV file.

    Args:
        matches (list): List of url agency matches.
    """
    fieldnames = [
        "source_url",
        "agency_name",
        "agency_url",
        "state",
        "county",
        "municipality",
        "agency_type",
        "jurisdiction_type",
    ]

    with open("results.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for match in matches:
            source_url = match["url"]

            if match["agency"]:
                agency_name = match["agency"]["name"]
                agency_url = match["agency"]["homepage_url"]
                state = match["agency"]["state_iso"]
                county = match["agency"]["county_name"]
                municipality = match["agency"]["municipality"]
                agency_type = match["agency"]["agency_type"]
                jurisdiction_type = match["agency"]["jurisdiction_type"]

                writer.writerow(
                    {
                        "source_url": source_url,
                        "agency_name": agency_name,
                        "agency_url": agency_url,
                        "state": state,
                        "county": county,
                        "municipality": municipality,
                        "agency_type": agency_type,
                        "jurisdiction_type": jurisdiction_type,
                    }
                )
            else:
                writer.writerow({"source_url": source_url})


def main():
    urls = get_urls()
    agencies = get_agencies_data()

    # Filter out agencies without a homepage_url set
    agencies = [agency for agency in agencies if agency["homepage_url"]]
    # Sort by count_data_sources, agencies with more data sources will be matched first
    agencies.sort(key=lambda agency: agency["count_data_sources"], reverse=True)
    agency_hostnames = [parse_hostname(agency["homepage_url"]) for agency in agencies]

    print("Indentifying agencies...")

    matches = [match_agencies(agencies, agency_hostnames, url) for url in tqdm(urls)]

    num_matches = len([matched_agency["agency"] for matched_agency in matches if matched_agency["agency"]])
    num_urls = len(urls)
    percent = 100 * float(num_matches) / float(num_urls)
    print(f"\n{num_matches} / {num_urls} ({percent:0.1f}%) of urls identified")

    write_csv(matches)

    print("Results written to results.csv")


if __name__ == "__main__":
    main()
