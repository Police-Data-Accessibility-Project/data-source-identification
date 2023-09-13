import csv
import os
import re
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from tqdm import tqdm


def get_urls(file=sys.argv[1]):
    with open(file, 'r') as f:
        urls = f.readlines()

    if file.endswith('.csv'):
        urls.pop(0)

    return urls


def get_agencies_data():
    # This is here for when the API is able to return all data from the agencies table
    # For now, the script will use PDAP Criminal Legal Agencies.csv
    #load_dotenv()
    #api_key = "Bearer " + os.getenv("PDAP_API_KEY")
    
    #response = requests.get("https://data-sources-app-bda3z.ondigitalocean.app/agencies", headers={"Authorization": api_key})
    #if response.status_code != 200:
    #    print("Request to PDAP API failed. Response code:", response.status_code)
    #    exit()
    #response_json = response.json()

    with open("PDAP Criminal Legal Agencies.csv", encoding="utf-8-sig") as agencies:
        agencies_list = list(csv.DictReader(agencies))

    return agencies_list


def parse_hostname(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc

    return hostname


def match_agencies(agencies, agency_hostnames, url):
    url = url.strip().strip('"')
    url_hostname = parse_hostname(url)

    if url_hostname in agency_hostnames:
        matched_agency = [agencies[agency_hostnames.index(agency_hostname)] for agency_hostname in agency_hostnames if url_hostname == agency_hostname]
    else:
        return {"url": url, "agency": []}

    if len(matched_agency) > 1:
        for agency in matched_agency:
            if (url.startswith(agency["homepage_url"])):
                matched_agency[0] = agency
                break
    
    return {"url": url, "agency": matched_agency[0]}


def write_csv(matches):
    fieldnames = ["source_url", "agency_name", "state", "county", "municipality", "agency_type", "jurisdiction_type"]

    with open("results.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for match in matches:
            source_url = match["url"]
            
            if match["agency"]:
                agency_name = match["agency"]["name"]
                state = match["agency"]["state_iso"]
                county = match["agency"]["county_name"]
                municipality = match["agency"]["municipality"]
                agency_type = match["agency"]["agency_type"]
                jurisdiction_type = match["agency"]["jurisdiction_type"]

                writer.writerow(
                    {
                        "source_url": source_url,
                        "agency_name": agency_name,
                        "state": state,
                        "county": county,
                        "municipality": municipality,
                        "agency_type": agency_type,
                        "jurisdiction_type": jurisdiction_type
                    }
                )
            else:
                writer.writerow({"source_url": source_url})
            

def main():
    urls = get_urls()
    agencies = get_agencies_data()

    agencies = [agency for agency in agencies if agency["homepage_url"]]
    agency_hostnames = [parse_hostname(agency["homepage_url"]) for agency in agencies]

    print("Indentifying agencies...")

    matches = [match_agencies(agencies, agency_hostnames, url) for url in tqdm(urls)]

    num_matches = len([matched_agency["agency"] for matched_agency in matches if matched_agency["agency"]])
    num_urls = len(urls)
    percent = 100 * float(num_matches) / float(num_urls)
    print(f"{num_matches} / {num_urls} ({percent:0.1f}%) of urls identified")

    write_csv(matches)

    print("Results written to results.csv")

if __name__ == '__main__':
    main()
