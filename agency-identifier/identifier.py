import csv
import re
import sys


def get_urls(file=sys.argv[1]):
    with open(file, 'r') as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]

    if file.endswith('.csv'):
        urls.pop(0)

    return urls


def get_agencies_data():
    with open("PDAP Criminal Legal Agencies.csv", encoding="utf-8-sig") as agencies:
        agencies_list = list(csv.DictReader(agencies))

    return agencies_list


def match_agencies(agencies, urls):
    matches = []

    for url in urls:
        matched_agency = [agency for agency in agencies if url.startswith(agency["homepage_url"])]

        if not matched_agency:
            pass
        
        if len(matched_agency) > 0:
            matched_agency = matched_agency[0]

        matches.append({"url": url, "agency": matched_agency})

    return matches 


def main():
    urls = get_urls()
    agencies = get_agencies_data()

    agencies = [agency for agency in agencies if agency["homepage_url"] and re.search("\.gov/|\.us/", agency["homepage_url"])]

    matches = match_agencies(agencies, urls)

    print(matches)

if __name__ == '__main__':
    main()