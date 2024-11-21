"""This program identifies if a given URL is a CKAN-hosted website"""
import re

from bs4 import BeautifulSoup
from from_root import from_root
import requests


def is_ckan_hosted(url):
    head = requests.get(url)
    soup = BeautifulSoup(head.content, "lxml")
    
    ckan_tag = soup.head.find(content=re.compile("ckan \d+\.\d+\.\d+"))
    if ckan_tag is not None:
        return True
    
    return False


def main():
    url = "https://www.w3schools.com/python/python_regex.asp"
    print(is_ckan_hosted(url))


if __name__ == "__main__":
    main()
    