import csv
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


def main():
    urls = get_urls()
    agencies = get_agencies_data()

    print(agencies[0])


if __name__ == '__main__':
    main()