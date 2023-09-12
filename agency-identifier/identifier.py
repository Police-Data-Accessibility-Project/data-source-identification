import csv
import re
import sys
from urllib.parse import urlparse
from time import perf_counter

#from sitemap_scraper.updated_sitemap_spider import core as sitemap_scraper


def get_urls(file=sys.argv[1]):
    with open(file, 'r') as f:
        urls = f.readlines()

    if file.endswith('.csv'):
        urls.pop(0)

    return urls


def get_agencies_data():
    with open("PDAP Criminal Legal Agencies.csv", encoding="utf-8-sig") as agencies:
        agencies_list = list(csv.DictReader(agencies))

    return agencies_list


def match_agencies(agencies, urls):
    matches = []
    unique_hostnames = []

    for url in urls:
        url = url.strip().strip('"')
        #url_hostname = parse_hostname(url)
        matched_agency = []

        #matched_agency = [agency for agency in agencies if url_hostname == parse_hostname(agency["homepage_url"])]
        
        #if len(matched_agency) > 1:
         #   for agency in matched_agency:
          #      if (url.startswith(agency["homepage_url"])):
           #         matched_agency[0] = agency
            #        break
        
        #matches.append({"url": url, "agency": matched_agency})
        #continue

        for agency in agencies:
            if url.startswith(agency["homepage_url"]):
                matched_agency = agency
                break

        if matched_agency:
            matches.append({"url": url, "agency": matched_agency})
            continue

        url_hostname = parse_hostname(url)

        if matched_hostname := [hostname for hostname in unique_hostnames if hostname["hostname"] == url_hostname]:
            matched_agency = matched_hostname[0]["agency"]
            matches.append({"url": url, "agency": matched_agency})
            continue
        
        for agency in agencies:
            agency_hostname = parse_hostname(agency["homepage_url"])

            if url_hostname == agency_hostname:
                matched_agency = agency
                unique_hostnames.append({"hostname": url_hostname, "agency": agency})
                break

        matches.append({"url": url, "agency": matched_agency})
    print(len(unique_hostnames))
    return matches 


def parse_hostname(url):
    parsed_url = urlparse(url)
    hostname = f"{parsed_url.scheme}://{parsed_url.netloc}/"

    return hostname


def main():
    urls = get_urls()
    agencies = get_agencies_data()

    agencies = [agency for agency in agencies if agency["homepage_url"]] #and re.search("\.gov/|\.us/", agency["homepage_url"])]
    start = perf_counter()
    matches = match_agencies(agencies, urls)
    print("Time:", perf_counter() - start)
    #print(matches)
    print(len([matched_agency["agency"] for matched_agency in matches if matched_agency["agency"]]), "/", len(urls))


if __name__ == '__main__':
    main()
