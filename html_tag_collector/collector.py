import json
import ssl
import urllib3
import urllib.request
from concurrent.futures import as_completed, ThreadPoolExecutor
import traceback

import requests
from requests_html import AsyncHTMLSession
import asyncio
import pyppeteer
from tqdm import tqdm
from tqdm.asyncio import tqdm
import bs4
from bs4 import BeautifulSoup
import sys
import polars as pl

from html_tag_collector.RootURLCache import RootURLCache

# Define the list of header tags we want to extract
header_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
DEBUG = False # Set to True to enable debug output
VERBOSE = True # Set to True to print dataframe each batch

# Define a function to process a URL and update the JSON object
def process_urls(df, render_javascript=False):
    """Process a list of urls and retrieve their HTML tags.

    Args:
        df (polars dataframe): contains url column with relevant urls
        render_javascript (bool): Whether or not to render webpage's JavaScript rendered HTML. Default is False.

    Returns:
        list: List of dicts with HTML tags.
    """

    urls = df.select(pl.col("url")).rows()
    new_urls = ["https://" + url[0] if not url[0].startswith("http") else url[0] for url in urls]
    
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)
    future = asyncio.ensure_future(run_get_response(new_urls))
    loop.run_until_complete(future)
    results = future.result()

    results.sort(key=lambda d: d["index"])
    urls_and_responses = [{"index": result["index"], "url": urls[i], "response": result["response"]} for i, result in enumerate(results)]
    
    if render_javascript:
        future = asyncio.ensure_future(render_js(urls_and_responses))
        loop.run_until_complete(future)
        results = future.result()

    parsed_data = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        print("Parsing responses...")
        future_to_tags = [executor.submit(parse_response, url_response) for url_response in urls_and_responses]

        for future in tqdm(as_completed(future_to_tags), total=len(future_to_tags)):
            data = future.result()
            parsed_data.append(data)

    urls_and_headers = sorted(parsed_data, key=lambda d: d["index"])
    [url_headers.pop("index") for url_headers in urls_and_headers]
    header_tags_df = pl.DataFrame(urls_and_headers)
    clean_header_tags_df = header_tags_df.with_columns(pl.col(["html_title", "meta_description"]).fill_null(""))

    return clean_header_tags_df


def exception_handler(loop, context):
    if DEBUG:
        msg = context.get("exception", context["message"])
        print(msg)


async def run_get_response(urls):
    """Asynchronously retrieves responses from a list of urls.

    Args:
        urls (list): List of urls.

    Returns:
        Future: Future with Response objects.
    """    
    tasks = []
    urllib3.disable_warnings()
    session = AsyncHTMLSession(workers=100)

    print("Retrieving HTML tags...")
    for i, url in enumerate(urls):
        task = asyncio.ensure_future(get_response(session, url, i))
        tasks.append(task)
    
    results = await tqdm.gather(*tasks)

    await session.close()
    return results


async def get_response(session, url, index):
    """Retrieves GET response for given url.

    Args:
        session (AsyncHTMLSession): Browser session used to retreive responses.
        url (str): Url to request.
        index (int): Index of the url to keep results in the same order.

    Returns:
        dict(int, Response): Dictionary of the url's index value and Response object, None if an error occurred.
    """
    headers = {
        # Some websites refuse the connection of automated requests, setting the User-Agent will circumvent that
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        # Make sure there's no pre-mature closing of responses before a redirect completes
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    response = None
    url = url.removesuffix(".json")

    try:
        response = await session.get(url, headers=headers, timeout=120)
    except requests.exceptions.SSLError:
        # This error is raised when the website uses a legacy SSL version, which is not supported by requests
        if DEBUG:
            print("SSLError:", url)

        # Retry without SSL verification
        response = await session.get(url, headers=headers, timeout=120, verify=False)
    except requests.exceptions.ConnectionError:
        # Sometimes this error is raised because the provided url uses http when it should be https and the website does not handle it properly
        if DEBUG:
            print("MaxRetryError:", url)

        if not url[4] == "s":
            url = url[:4] + "s" + url[4:]
            # Retry with https
            response = await session.get(url, headers=headers, timeout=120)
    except (urllib3.exceptions.LocationParseError, requests.exceptions.ReadTimeout) as e:
        if DEBUG:
            print(f"{type(e).__name__}: {url}")
    except Exception as e:
        if DEBUG:
            print("Exception:", url)
            print(traceback.format_exc())
            print(str(e))
    finally:
        if DEBUG:
           print(url, response)

        return {"index": index, "response": response}


async def render_js(urls_responses):
    """Renders JavaScript from a list of urls.

    Args:
        urls_responses (dict): Dictionary containing urls and their responses.
    """
    print("Rendering JavaScript...")
    for url_response in tqdm(urls_responses):
        res = url_response["response"]

        if res is not None and res.ok:
            if DEBUG:
                print("Rendering", url_response["url"][0])
            task = asyncio.create_task(res.html.arender())
            
            # Some websites will cause the rendering to hang indefinitely so we cancel the task if more than 15 seconds have elapsed
            time_elapsed = 0
            while not task.done():
                time_elapsed += 1
                await asyncio.sleep(0.1)

                if time_elapsed > 150:
                    task.cancel()
                    break
            
            try:
                await task
            except (pyppeteer.errors.PageError, pyppeteer.errors.NetworkError) as e:
                if DEBUG:
                    print(f"{type(e).__name__}")
            except Exception as e:
                if DEBUG:
                    print(traceback.format_exc())
                    print(str(e))
            except asyncio.CancelledError:
                if DEBUG:
                    print("Rendering cancelled")

root_url_cache = RootURLCache()

def parse_response(url_response):
    """Parses relevant HTML tags from a Response object into a dictionary.

    Args:
        url_response (list[dict]): List of dictionaries containing urls and theeir responses.

    Returns:
        list[dict]: List of dictionaries containing urls and relevant HTML tags.
    """
    tags = {}
    res = url_response["response"]
    tags["index"] = url_response["index"]
    tags["url"] = url_response["url"][0]

    if res is None:
        tags["http_response"] = -1
        return tags

    tags["http_response"] = res.status_code
    if not res.ok:
        return tags

    try:
        soup = BeautifulSoup(res.html.html, "html.parser")
    except (bs4.builder.ParserRejectedMarkup, AssertionError):
        return tags

    tags["html_title"] = soup.title.string if soup.title is not None else ""
    tags["root_page_title"] = root_url_cache.get_title(tags["url"])

    meta_tag = soup.find("meta", attrs={"name": "description"})
    try:
        tags["meta_description"] = meta_tag["content"] if meta_tag is not None else ""
    except KeyError:
        tags["meta_description"] = ""

    for header_tag in header_tags:
        headers = soup.find_all(header_tag)
        header_content = [header.text for header in headers]
        tags[header_tag] = json.dumps(header_content)

    return tags


def collector_main(df, render_javascript=False):
    header_tags_df = process_urls(df, render_javascript=render_javascript)

    return header_tags_df

def process_in_batches(df, batch_size=200):
    """ Runs the tag collector on small batches of URLs contained in df

    Args: 
        df: polars dataframe containing all URLs in a 'url' column
        batch_size: (int) # of URLs to process at a time (default 200)

    Returns:
        cumulative_df: polars dataframe containing responses from all batches

    """
          
    # Create an empty DataFrame to store the final cumulative result
    cumulative_df = pl.DataFrame()

    # Calculate the number of batches needed
    num_batches = (len(df) + batch_size - 1) // batch_size

    print(f"\nTotal samples: {len(df)}")
    print(f"Batch size: {batch_size}")
    print(f"Number of Batches: {num_batches} \n")

    # Process the DataFrame in batches
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(df))
        batch_df = df[start_idx:end_idx]

        print(f"\nBatch {i + 1}/{num_batches}")

        # Call the collector_main function on the current batch
        header_tags_df = collector_main(batch_df)

        # Check if it's the first batch, then directly set result_df
        # if not then append latest batch on bottom
        if i == 0:
            cumulative_df = header_tags_df
        else:
            cumulative_df = pl.concat([cumulative_df, header_tags_df], how='vertical')

    return cumulative_df


if __name__ == '__main__':
    # Open the input file and load the JSON data
    with open(sys.argv[1]) as f:
        data = json.load(f)

    df = pl.DataFrame(data)
    
    #returns cumulative dataframe (contains all batches) of url and headers tags
    cumulative_df = process_in_batches(df)

    #join the url/header tag df with the original df which contains the labels (order has been preserved)
    #remove duplicate rows
    out_df = df.join(cumulative_df, on='url', how='left')
    out_df = out_df.unique(subset=['id'], maintain_order=True)

    if VERBOSE: print(out_df)

    # Write the updated JSON data to a new file
    out_df.write_csv('labeled-urls-headers.csv')
