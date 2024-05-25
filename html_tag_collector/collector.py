import json
import ssl
import urllib3
import urllib.request
from concurrent.futures import as_completed, ThreadPoolExecutor
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
from urllib.parse import urlparse

from RootURLCache import RootURLCache
from common import get_user_agent
from DataClassTags import Tags


# Define the list of header tags we want to extract
header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
DEBUG = False  # Set to True to enable debug output
VERBOSE = False  # Set to True to print dataframe each batch
root_url_cache = RootURLCache()


def process_urls(manager_list, render_javascript):
    """Process a list of urls and retrieve their HTML tags.

    Args:
        manager_list (shared list[polars dataframe]): shared list containing the polars dataframe, used to send and retrieve data from outside the current process.
        render_javascript (bool): Whether or not to render webpage's JavaScript rendered HTML.

    Returns:
        list: List of dicts with HTML tags.
    """
    df = manager_list[0]
    urls = df.select(pl.col("url")).rows()
    new_urls = []
    for url in urls:
        if url[0] is not None and not url[0].startswith("http"):
            new_urls.append("https://" + url[0])
        else:
            new_urls.append(url[0])

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

    urls_and_headers = []
    print("Parsing responses...")
    for url_response in tqdm(urls_and_responses):
        urls_and_headers.append(parse_response(url_response))

    [url_headers.pop("index") for url_headers in urls_and_headers]
    header_tags_df = pl.DataFrame(urls_and_headers)
    clean_header_tags_df = header_tags_df.with_columns(pl.all().fill_null(""))

    # Return updated DataFrame
    manager_list[0] = clean_header_tags_df


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
    session = AsyncHTMLSession(workers=100, browser_args=["--no-sandbox", f"--user-agent={get_user_agent()}"])

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
        "User-Agent": get_user_agent(),
        # Make sure there's no pre-mature closing of responses before a redirect completes
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    response = None
    if url is not None:
        url = url.removesuffix(".json")

    try:
        response = await session.get(url, headers=headers, timeout=120)
    except (requests.exceptions.SSLError, ssl.SSLError):
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

        content_type = None
        try:
            content_type = response.headers["content-type"]
        except (KeyError, AttributeError):
            pass

        # If the response size is greater than 10 MB
        # or the response is an unreadable content type
        # or the response code from the website is not in the 200s
        if (
            response is not None and len(response.content) > 10000000
            or content_type is not None and any(
                filtered_type in content_type
                for filtered_type in ["pdf", "excel", "msword", "image", "rtf", "zip", "octet", "csv", "json"]
            )
            or response is not None and not response.ok
        ):
            # Discard the response content to prevent out of memory errors
            if DEBUG:
                print("Large or unreadable content discarded:", len(response.content), url)
            new_response = requests.Response()
            new_response.status_code = response.status_code
            response = new_response

        return {"index": index, "response": response}


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
        Tags: DataClass containing the url and relevant HTML tags.
    """
    #remove_excess_whitespace = lambda s: " ".join(s.split()).strip()
    
    tags = {}
    tags_test = Tags()
    res = url_response["response"]
    #tags["index"] = url_response["index"]
    tags_test.index = url_response["index"]

    # Drop hostname from urls to reduce training bias
    '''url = url_response["url"][0]
    tags["url"] = url
    if not url.startswith("http"):
        url = "https://" + url
    tags["url_path"] = urlparse(url).path[1:]'''
    tags_test = get_url(tags_test, url_response)

    #tags["html_title"] = ""
    #tags["meta_description"] = ""
    #tags["root_page_title"] = remove_excess_whitespace(root_url_cache.get_title(tags["url"]))

    # The response is None if there was an error during connection, meaning there is no content to read
    if res is None:
        #tags["http_response"] = -1
        return tags

    # If the connection did not return a 300 code, we can assume there is no relevant content to read
    #tags["http_response"] = res.status_code
    tags_test.http_response = res.status_code
    if not res.ok:
        return tags

    # Attempt to read the content-type, set the parser accordingly to avoid warning messages
    try:
        content_type = res.headers["content-type"]
    except KeyError:
        return tags
    # If content type does not contain "html" or "xml" then we can assume that the content is unreadable
    if "html" in content_type:
        parser = "lxml"
    elif "xml" in content_type:
        parser = "lxml-xml"
    else:
        return tags

    try:
        soup = BeautifulSoup(res.html.html, parser)
    except (bs4.builder.ParserRejectedMarkup, AssertionError, AttributeError):
        return tags

    '''if soup.title is not None and soup.title.string is not None:
        tags["html_title"] = remove_excess_whitespace(soup.title.string)
    else:
        tags["html_title"] = ""'''
    tags_test = get_html_title(tags_test, soup)

    '''meta_tag = soup.find("meta", attrs={"name": "description"})
    try:
        tags["meta_description"] = remove_excess_whitespace(meta_tag["content"]) if meta_tag is not None else ""
    except KeyError:
        tags["meta_description"] = ""'''
    tags_test = get_meta_description(tags_test, soup)

    '''for header_tag in header_tags:
        headers = soup.find_all(header_tag)
        # Retreives and drops headers containing links to reduce training bias
        header_content = [header.get_text(" ", strip=True) for header in headers if not header.a]
        tags[header_tag] = json.dumps(header_content, ensure_ascii=False)'''
    tags_test = get_header_tags(tags_test, soup)

    # Extract max 500 words of text from HTML <div>'s
    '''div_text = ""
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
    tags["div_text"] = div_text[:MAX_WORDS * 10]'''
    tags_test = get_div_text(tags_test, soup)
    print(tags_test)

    # Prevents most bs4 memory leaks
    if soup.html:
        soup.html.decompose()

    return tags


def get_url(tags, url_response):
    """Updates the Tags DataClass with the url and url_path.

    Args:
        tags (Tags): DataClass for relevant HTML tags.
        url_response (list[dict]): List of dictionaries containing urls and their responses.

    Returns:
        Tags: DataClass with updated url and url_path.
    """
    url = url_response["url"][0]
    tags.url = url
    if not url.startswith("http"):
        url = "https://" + url

    # Drop hostname from urls to reduce training bias
    url_path = urlparse(url).path[1:]
    # Remove trailing backslash
    if url_path[-1] == "/":
        url_path = url_path[:-1]
    tags.url_path = url_path

    return tags


def get_html_title(tags, soup):
    """Updates the Tags DataClass with the html_title.

    Args:
        tags (Tags): DataClass for relevant HTML tags.
        soup (BeautifulSoup): BeautifulSoup object to pull the HTML title from.

    Returns:
        Tags: DataClass with updated html_title.
    """
    if soup.title is not None and soup.title.string is not None:
        tags.html_title = remove_excess_whitespace(soup.title.string)
    
    return tags


def get_meta_description(tags, soup):
    """Updates the Tags DataClass with the meta_description.

    Args:
        tags (Tags): DataClass for relevant HTML tags.
        soup (BeautifulSoup): BeautifulSoup object to pull the meta description from.

    Returns:
        Tags: DataClass with updated meta_description.
    """    
    meta_tag = soup.find("meta", attrs={"name": "description"})
    try:
        tags.meta_description = remove_excess_whitespace(meta_tag["content"]) if meta_tag is not None else ""
    except KeyError:
        return
    
    return tags


def get_header_tags(tags, soup):
    """Updates the Tags DataClass with the header tags.

    Args:
        tags (Tags): DataClass for relevant HTML tags.
        soup (BeautifulSoup): BeautifulSoup object to pull the header tags from.

    Returns:
        Tags: DataClass with updated header tags.
    """    
    for header_tag in header_tags:
        headers = soup.find_all(header_tag)
        # Retreives and drops headers containing links to reduce training bias
        header_content = [header.get_text(" ", strip=True) for header in headers if not header.a]
        tag_content = json.dumps(header_content, ensure_ascii=False)
        setattr(tags, header_tag, tag_content)

    return tags


def get_div_text(tags, soup):
    """Updates the Tags DataClass with the div_text.

    Args:
        tags (Tags): DataClass for relevant HTML tags.
        soup (BeautifulSoup): BeautifulSoup object to pull the div text from.

    Returns:
        Tags: DataClass with updated div_text.
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
    tags.div_text = div_text[:MAX_WORDS * 10]

    return tags


def remove_excess_whitespace(s):
    """Removes leading, trailing, and excess adjacent whitespace.

    Args:
        s (str): String to remove whitespace from.

    Returns:
        str: Clean string with excess whitespace stripped.
    """    
    return " ".join(s.split()).strip()


def collector_main(df, render_javascript=False):
    context = multiprocessing.get_context("spawn")
    manager = context.Manager()
    manager_list = manager.list([df])

    process = context.Process(target=process_urls, args=(manager_list, render_javascript))
    process.start()
    process.join()

    return manager_list[0]


def process_in_batches(df, render_javascript=False, batch_size=200):
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


if __name__ == "__main__":
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
        render_javascript = True

    # returns cumulative dataframe (contains all batches) of url and headers tags
    cumulative_df = process_in_batches(df, render_javascript=render_javascript)

    # Drop duplicate columns
    df = df.drop(["http_response", "html_title", "meta_description", "root_page_title", *header_tags])
    # join the url/header tag df with the original df which contains the labels (order has been preserved)
    # remove duplicate rows
    out_df = df.join(cumulative_df, on="url", how="left")
    out_df = out_df.unique(subset=["url"], maintain_order=True)

    if VERBOSE:
        print(out_df)

    # Write the updated JSON data to a new file
    out_df.write_csv("labeled-source-text.csv")
