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


# Define the list of header tags we want to extract
header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
DEBUG = False  # Set to True to enable debug output
VERBOSE = False  # Set to True to print dataframe each batch


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
    new_urls = ["https://" + url[0] if not url[0].startswith("http") else url[0] for url in urls]

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
        url_response (list[dict]): List of dictionaries containing urls and theeir responses.

    Returns:
        list[dict]: List of dictionaries containing urls and relevant HTML tags.
    """
    tags = {}
    res = url_response["response"]
    tags["index"] = url_response["index"]
    tags["url"] = url_response["url"][0]
    tags["html_title"] = ""
    tags["meta_description"] = ""

    if res is None:
        tags["http_response"] = -1
        return tags

    tags["http_response"] = res.status_code
    if not res.ok:
        return tags

    try:
        content_type = res.headers["content-type"]
    except KeyError:
        return tags

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

    tags["html_title"] = soup.title.string.strip() if soup.title is not None else ""

    meta_tag = soup.find("meta", attrs={"name": "description"})
    try:
        tags["meta_description"] = meta_tag["content"] if meta_tag is not None else ""
    except KeyError:
        tags["meta_description"] = ""

    for header_tag in header_tags:
        headers = soup.find_all(header_tag)
        header_content = [header.get_text(" ", strip=True) for header in headers]
        tags[header_tag] = json.dumps(header_content, ensure_ascii=False)

    # Prevents most bs4 memory leaks
    if soup.html:
        soup.html.decompose()

    return tags


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
    df = df.drop(["http_response", "html_title", "meta_description", *header_tags])
    # join the url/header tag df with the original df which contains the labels (order has been preserved)
    # remove duplicate rows
    out_df = df.join(cumulative_df, on="url", how="left")
    out_df = out_df.unique(subset=["url"], maintain_order=True)

    if VERBOSE:
        print(out_df)

    # Write the updated JSON data to a new file
    out_df.write_csv("labeled-urls-headers.csv")
