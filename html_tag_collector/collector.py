import json
import requests
from bs4 import BeautifulSoup
import sys
import polars as pl

# Define the list of header tags we want to extract
header_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

# Define a function to process a URL and update the JSON object
def process_url(url):
    try:
        response = requests.get(url, timeout=10)
    except (requests.exceptions.ConnectionError, requests.exceptions.RequestException):
        print(f"Error: Invalid URL - {url}")
        print("Invalid URLs removed from output data")
        return {}

    # Add the HTTP response status code as a new property
    # If the response status code is not in the 200 range, skip adding other properties
    if not response.ok:
        return {}

    # Check if the URL ends with .pdf
    if url.endswith('.pdf'):
        return {}
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title tag and its content
    html_title = soup.title.string if soup.title is not None else ""

    # Extract the meta description tag and its content
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    meta_description = meta_tag['content'] if meta_tag is not None else ""

    output = [html_title, meta_description]
    # Extract the header tags and their content
    for header_tag in header_tags:
        headers = soup.find_all(header_tag)
        header_content = ",".join([header.text for header in headers])
        output.append(header_content)

    return output


def collector_main(df):
    # Loop over each URL in the data
    df = df.select([pl.col("*"), pl.col("url").apply(process_url).alias("all_fields")])
    df = df.with_columns([pl.col("all_fields").apply(lambda af: af[0]).alias("html_title"),
        pl.col("all_fields").apply(lambda af: af[1]).alias("meta_description")])
    pos = 2
    # for h in header_tags:
    #     df = df.with_columns([pl.col("all_fields").apply(lambda af: af[pos]).alias(h)])
    #     pos += 1

    return df


if __name__ == '__main__':
    # Open the input file and load the JSON data
    if sys.argv[1]:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        df = pl.DataFrame(data)
    
    output_data = collector_main(df)

    if sys.argv[1]:
        # Write the updated JSON data to a new file
        output_data.to_csv('urls_and_headers.csv', index=False)