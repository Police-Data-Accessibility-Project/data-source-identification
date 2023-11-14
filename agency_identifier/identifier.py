import csv
import os
import sys
from urllib.parse import urlparse
import requests
import polars as pl
import tqdm

def get_agencies_data():
    """Retrives a list of agency dictionaries from file.

    Returns:
        list: List of agency dictionaries.
    """
    api_key = "Bearer " + os.getenv("PDAP_API_KEY")

    results = {"data": {}}
    page = 1
    agencies_df = pl.DataFrame()
    while results:
        #print(page)
        response = requests.get(f"https://data-sources.pdap.io/api/agencies/{page}", headers={"Authorization": api_key})
        if response.status_code != 200:
            print("Request to PDAP API failed. Response code:", response.status_code)
            exit()
        results = response.json()["data"]
        fields = ["defunct_year", "data_sources", "airtable_agency_last_modified", "agency_created", "data_sources_last_updated"]
        for r in results:
            for f in fields:
                r[f] = "" if r[f] is None else r[f]

        new_agencies_df = pl.DataFrame(results)
        if not new_agencies_df.is_empty():
            agencies_df = pl.concat([agencies_df, new_agencies_df])
        page += 1   

    return agencies_df


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
        return {"url": url, "agency": [], "status": "No match found"}

    # More than one agency was found
    if len(matched_agency) > 1:
        url_no_http = remove_http(url)

        for agency in matched_agency:
            agency_homepage = remove_http(agency["homepage_url"])
            # It is assumed that if the url begins with the agency's url, then it belongs to that agency
            if url_no_http.startswith(agency_homepage):
                return {"url": url, "agency": agency, "status": "Match found"}
                break
        
        return {"url": url, "agency": [], "status": "Contested match"}

    return {"url": url, "agency": matched_agency[0], "status": "Match found"}


# def write_csv(matches):
#     """Write matches to a CSV file.

#     Args:
#         matches (list): List of url agency matches.
#     """
#     fieldnames = [
#         "source_url",
#         "status",
#         "agency_name",
#         "agency_url",
#         "state",
#         "county",
#         "municipality",
#         "agency_type",
#         "jurisdiction_type",
#     ]

#     with open("results.csv", "w", newline="") as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#         writer.writeheader()

#         for match in matches:
#             source_url = match["url"]
#             status = match["status"]

#             if match["agency"]:
#                 agency_name = match["agency"]["name"]
#                 agency_url = match["agency"]["homepage_url"]
#                 state = match["agency"]["state_iso"]
#                 county = match["agency"]["county_name"]
#                 municipality = match["agency"]["municipality"]
#                 agency_type = match["agency"]["agency_type"]
#                 jurisdiction_type = match["agency"]["jurisdiction_type"]

#                 writer.writerow(
#                     {
#                         "source_url": source_url,
#                         "status": status,
#                         "agency_name": agency_name,
#                         "agency_url": agency_url,
#                         "state": state,
#                         "county": county,
#                         "municipality": municipality,
#                         "agency_type": agency_type,
#                         "jurisdiction_type": jurisdiction_type,
#                     }
#                 )
#             else:
#                 writer.writerow(
#                     {
#                         "source_url": source_url,
#                         "status": status
#                     }
#                 )


def identifier_main(urls_df):
    agencies_df = get_agencies_data()
    # Filter out agencies without a homepage_url set
    agencies_df = agencies_df.filter(pl.col("homepage_url").is_not_null())
    agencies_df = agencies_df.with_columns(pl.col("homepage_url").map_elements(parse_hostname).alias("hostname"),
        pl.col("count_data_sources").fill_null(0))
    agencies_df = agencies_df.with_columns(pl.col("count_data_sources").max().over("hostname").alias("max_data_sources")).filter(pl.col("count_data_sources") == pl.col("max_data_sources"))
    agencies_df = agencies_df.unique(subset=["homepage_url"])
    print(agencies_df.filter(pl.col("homepage_url").is_duplicated()).sort("homepage_url"))

    print("Indentifying agencies...")
    urls_df = urls_df.with_columns(pl.col("url").map_elements(parse_hostname).alias("hostname"))
    matched_agencies_df = urls_df.join(agencies_df, on="hostname", how='left')
    matched_agencies_clean_df = matched_agencies_df.with_columns(pl.all().fill_null(""))

    return matched_agencies_clean_df


if __name__ == "__main__":
    urls_df = pl.read_csv(sys.argv[1])
    matched_agencies_df = identifier_main(urls_df)

    matches_only = matched_agencies_df.filter(pl.col("hostname").is_not_null())

    num_matches = len(matches_only)
    num_urls = len(urls_df)
    percent = 100 * float(num_matches) / float(num_urls)
    print(f"\n{num_matches} / {num_urls} ({percent:0.1f}%) of urls identified")

    if not matches_only.is_empty():
        matches_only.select(pl.col("url"),
            pl.col("name"),
            pl.col("state_iso"),
            pl.col("county_name"),
            pl.col("municipality"),
            pl.col("agency_type"),
            pl.col("jurisdiction_type"),
            pl.col("approved")).write_csv('results.csv')

    print("Results written to results.csv")