""" The tag collector is used to collect HTML tags and other relevant data from websites that is useful for training prediction models.
    Information being collected includes:
        - The URL's path
        - HTML title
        - Meta description
        - The root page's HTML title
        - HTTP response code
        - Contents of H1-H6 header tags
        - Contents of div tags
"""


from dataclasses import asdict
from collections import namedtuple
import json
import urllib3
import sys
import traceback
import multiprocessing

import requests
from requests_html import AsyncHTMLSession
import asyncio
import pyppeteer
from tqdm import tqdm
from tqdm.asyncio import tqdm
import bs4
from bs4 import BeautifulSoup
import polars as pl

from html_tag_collector.DataClassTags import ResponseHTMLInfo
from html_tag_collector.ResponseFetcher import ResponseFetcher
from html_tag_collector.ResponseParser import ResponseParser, HTMLResponseParser
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.constants import USER_AGENT, HEADER_TAGS
from html_tag_collector.url_adjustment_functions import standardize_url_prefixes, remove_json_suffix, \
    add_https, remove_trailing_backslash, drop_hostname
from html_tag_collector.util import remove_excess_whitespace

# Define the list of header tags we want to extract
DEBUG = False  # Set to True to enable debug output
VERBOSE = False  # Set to True to print dataframe each batch
root_url_cache = RootURLCache()


def process_urls(manager_list: list[pl.DataFrame], render_javascript: bool):
    """Process a list of urls and retrieve their HTML tags.

    Args:
        manager_list (shared list[polars dataframe]): shared list containing the polars dataframe, used to send and retrieve data from outside the current process.
        render_javascript (bool): Whether or not to render webpage's JavaScript rendered HTML.

    Returns:
        list: List of dicts with HTML tags.
    """
    df = manager_list[0]
    urls = df.select(pl.col("url")).rows()
    new_urls = standardize_url_prefixes(urls)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)
    future = asyncio.ensure_future(run_get_response(new_urls))
    loop.run_until_complete(future)
    results = future.result()

    results.sort(key=lambda d: d["index"])
    urls_and_responses = [
        {"index": result["index"], "url": urls[i], "response": result["response"]} for i, result in enumerate(results)
    ]

    if render_javascript:
        future = asyncio.ensure_future(render_js(urls_and_responses))
        loop.run_until_complete(future)
        results = future.result()

    urls_and_headers = get_urls_and_headers(urls_and_responses)

    remove_indices(urls_and_headers)
    clean_header_tags_df = get_header_tags_df(urls_and_headers)

    # Return updated DataFrame
    manager_list[0] = clean_header_tags_df


def get_header_tags_df(urls_and_headers):
    header_tags_df = pl.DataFrame(urls_and_headers)
    clean_header_tags_df = header_tags_df.with_columns(pl.all().fill_null(""))
    return clean_header_tags_df


def get_urls_and_headers(urls_and_responses):
    urls_and_headers = []
    print("Parsing responses...")
    for url_response in tqdm(urls_and_responses):
        urls_and_headers.append(parse_response(url_response))
    return urls_and_headers


def remove_indices(urls_and_headers):
    [url_headers.pop("index") for url_headers in urls_and_headers]



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
    session = AsyncHTMLSession(workers=100, browser_args=["--no-sandbox", f"--user-agent={USER_AGENT}"])

    print("Retrieving HTML tags...")
    for i, url in enumerate(urls):
        task = asyncio.ensure_future(get_response(session, url, i))
        tasks.append(task)

    results = await tqdm.gather(*tasks)

    await session.close()
    return results


async def get_response(session: AsyncHTMLSession, url, index):
    """Retrieves GET response for given url.

    Args:
        session (AsyncHTMLSession): Browser session used to retreive responses.
        url (str): Url to request.
        index (int): Index of the url to keep results in the same order.

    Returns:
        dict(int, Response): Dictionary of the url's index value and Response object, None if an error occurred.
    """
    url = await remove_json_suffix(url)

    rf = ResponseFetcher(session, url, debug=DEBUG)
    response = await rf.get_response()
    content_type = await get_content_type(response)
    response = handle_invalid_response(response, content_type, rf.url)

    return {"index": index, "response": response}


# Resposne parser
async def get_content_type(response):
    content_type = None
    try:
        content_type = response.headers["content-type"]
    except (KeyError, AttributeError):
        pass
    return content_type




def handle_invalid_response(response, content_type, url):
    """Checks the response to see if content is too large, unreadable, or invalid response code. The response is discarded if it is invalid.

    Args:
        response (Response): Response object to check.
        content_type (str): The content type returned by the website.
        url (str): URL that was requested.

    Returns:
        Response: The response object is returned either unmodified or discarded.
    """
    if response is None:
        return response
    valid = is_valid_response(content_type, response)
    if not valid:
        # Discard the response content to prevent out of memory errors
        if DEBUG:
            print("Large or unreadable content discarded:", len(response.content), url)
        new_response = requests.Response()
        new_response.status_code = response.status_code
        response = new_response

    return response


def is_valid_response(content_type, response):
    # If the response size is greater than 10 MB
    if len(response.content) > 10000000:
        return False
    # or the response is an unreadable content type
    if content_type is not None and any(
            filtered_type in content_type
            for filtered_type in ["pdf", "excel", "msword", "image", "rtf", "zip", "octet", "csv", "json"]
    ):
        return False
    # or the response code from the website is not in the 200s
    if not response.ok:
        return False
    return True


async def render_js(urls_responses):
    """Renders JavaScript from a list of urls.

    Args:
        urls_responses (dict): Dictionary containing urls and their responses.
    """
    print("Rendering JavaScript...")
    for url_response in tqdm(urls_responses):
        res = url_response["response"]

        if res is None or not res.ok:
            continue

        if DEBUG:
            print("Rendering", url_response["url"][0])
        try:
            task = asyncio.create_task(res.html.arender())
        except AttributeError:
            continue

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


def parse_response(url_response):
    """Parses relevant HTML tags from a Response object into a dictionary.

    Args:
        url_response (list[dict]): List of dictionaries containing urls and their responses.

    Returns:
        dict: Dictionary containing the url and relevant HTML tags.
    """
    rp = ResponseParser(
        url_response=url_response, root_url_cache=root_url_cache
    )
    return rp.parse()

    tags = ResponseHTMLInfo()
    # TODO: Convert URL Response to a class
    res = url_response["response"]
    tags.index = url_response["index"]

    tags.url, tags.url_path = get_url(url_response)

    tags.root_page_title = remove_excess_whitespace(root_url_cache.get_title(tags.url))

    verified, tags.http_response = verify_response(res)
    if verified is False:
        return asdict(tags)

    # Soup Methods
    parser = get_parser_type(res)
    if parser is False:
        return asdict(tags)

    try:
        soup = BeautifulSoup(res.html.html, parser)
    except (bs4.builder.ParserRejectedMarkup, AssertionError, AttributeError):
        return asdict(tags)

    tags.html_title = get_html_title(soup)

    tags.meta_description = get_meta_description(soup)

    tags = get_header_tags(tags, soup)

    tags.div_text = get_div_text(soup)

    # Prevents most bs4 memory leaks
    if soup.html:
        soup.html.decompose()

    return asdict(tags)


def get_url(url_response):
    """Returns the url and url_path.

    Args:
        url_response (list[dict]): List of dictionaries containing urls and their responses.

    Returns:
        (str, str): Tuple with the url and url_path.
    """
    # TODO: Does this part require the URL response? Or can it be done prior to the response?
    url = url_response["url"][0]
    new_url = url
    new_url = add_https(new_url)

    # Drop hostname from urls to reduce training bias
    url_path = drop_hostname(new_url)
    # Remove trailing backslash
    url_path = remove_trailing_backslash(url_path)

    return url, url_path


def verify_response(res):
    """Verifies the webpage response is readable and ok.

    Args:
        res (HTMLResponse|Response): Response object to verify.

    Returns:
        VerifiedResponse(bool, int): A named tuple containing False if verification fails, True otherwise and the http response code.
    """
    VerifiedResponse = namedtuple("VerifiedResponse", "verified http_response")
    # The response is None if there was an error during connection, meaning there is no content to read
    if res is None:
        return VerifiedResponse(False, -1)

    # If the connection did not return a 200 code, we can assume there is no relevant content to read
    http_response = res.status_code
    if not res.ok:
        return VerifiedResponse(False, http_response)

    return VerifiedResponse(True, http_response)


def get_parser_type(res):
    """Retrieves the parser type to use with BeautifulSoup.

    Args:
        res (HTMLResponse|Response): Response object to read the content-type from.

    Returns:
        str|bool: A string of the parser to use, or False if not readable.
    """
    # Attempt to read the content-type, set the parser accordingly to avoid warning messages
    try:
        content_type = res.headers["content-type"]
    except KeyError:
        return False

    # If content type does not contain "html" or "xml" then we can assume that the content is unreadable
    if "html" in content_type:
        parser = "lxml"
    elif "xml" in content_type:
        parser = "lxml-xml"
    else:
        return False

    return parser


def get_html_title(soup):
    """Retrieves the HTML title from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object to pull the HTML title from.

    Returns:
        str: The HTML title.
    """
    html_title = ""

    if soup.title is not None and soup.title.string is not None:
        html_title = remove_excess_whitespace(soup.title.string)

    return html_title


def get_meta_description(soup):
    """Retrieves the meta description from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object to pull the meta description from.

    Returns:
        str: The meta description.
    """
    meta_tag = soup.find("meta", attrs={"name": "description"})
    try:
        meta_description = remove_excess_whitespace(meta_tag["content"]) if meta_tag is not None else ""
    except KeyError:
        return ""

    return meta_description


def get_header_tags(tags, soup):
    """Updates the Tags DataClass with the header tags.

    Args:
        tags (ResponseHTMLInfo): DataClass for relevant HTML tags.
        soup (BeautifulSoup): BeautifulSoup object to pull the header tags from.

    Returns:
        ResponseHTMLInfo: DataClass with updated header tags.
    """
    for header_tag in HEADER_TAGS:
        headers = soup.find_all(header_tag)
        # Retrieves and drops headers containing links to reduce training bias
        header_content = [header.get_text(" ", strip=True) for header in headers if not header.a]
        tag_content = json.dumps(header_content, ensure_ascii=False)
        setattr(tags, header_tag, tag_content)

    return tags


def get_div_text(soup):
    """Retrieves the div text from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): BeautifulSoup object to pull the div text from.

    Returns:
        str: The div text.
    """
    # Extract max 500 words of text from HTML <div>'s
    div_text = ""
    MAX_WORDS = 500
    for div in soup.find_all("div"):
        text = div.get_text(" ", strip=True)
        if text:
            # Check if adding the current text exceeds the word limit
            if len(div_text.split()) + len(text.split()) <= MAX_WORDS:
                div_text += text + " "
            else:
                break  # Stop adding text if word limit is reached

    # Truncate to 5000 characters in case of run-on 'words'
    div_text = div_text[: MAX_WORDS * 10]

    return div_text


#region Uses Dataframe
def collector_main(df: pl.DataFrame, render_javascript=False):
    context = multiprocessing.get_context("spawn")
    manager = context.Manager()
    manager_list = manager.list([df])

    process = context.Process(target=process_urls, args=(manager_list, render_javascript))
    process.start()
    process.join()

    return manager_list[0]


def process_in_batches(df: pl.DataFrame, render_javascript=False, batch_size=200):
    """Runs the tag collector on small batches of URLs contained in df

    Args:
        df: polars dataframe containing all URLs in a 'url' column
        render_javascript (bool): Whether or not to render webpage's JavaScript rendered HTML.
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
        header_tags_df = collector_main(batch_df, render_javascript=render_javascript)

        # Check if it's the first batch, then directly set result_df
        # if not then append latest batch on bottom
        if i == 0:
            cumulative_df = header_tags_df
        else:
            cumulative_df = pl.concat([cumulative_df, header_tags_df], how="vertical")

    return cumulative_df


def combine_dataframes(df, cumulative_df):
    # Drop duplicate columns
    df = df.drop(["http_response", "html_title", "meta_description", "root_page_title", *HEADER_TAGS])
    # join the url/header tag df with the original df which contains the labels (order has been preserved)
    # remove duplicate rows
    out_df = df.join(cumulative_df, on="url", how="left")
    out_df = out_df.unique(subset=["url"], maintain_order=True)

    return out_df

#endregion

def main():
    # Open file
    file = sys.argv[1]
    if file.endswith(".json"):
        with open(file) as f:
            data = json.load(f)
        df = pl.DataFrame(data)
    elif file.endswith(".csv"):
        df = pl.read_csv(file)
    else:
        print("Unsupported filetype")
        sys.exit(1)
    render_javascript = False
    if len(sys.argv) > 2 and sys.argv[2] == "--render-javascript":
        # Render Javascript is always enabled when running in Source Collector Pipeline
        render_javascript = True
    # returns cumulative dataframe (contains all batches) of url and headers tags
    cumulative_df = process_in_batches(df, render_javascript=render_javascript)
    out_df = combine_dataframes(df, cumulative_df)
    if VERBOSE:
        print(out_df)
    # Write the updated JSON data to a new file
    out_df.write_csv("labeled-source-text.csv")


if __name__ == "__main__":
    main()
