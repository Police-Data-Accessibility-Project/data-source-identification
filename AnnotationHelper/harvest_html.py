import requests
import logging

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch HTML from {url}: {e}")
        return str(e)


def harvest_html(urls):
    html_content = {}
    for url in urls:
        try:
            html_content[url] = fetch_html(url)
        except Exception as e:
            logging.error(f"Failed to harvest HTML for {url}: {e}")
    return html_content

