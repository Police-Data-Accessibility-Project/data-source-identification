import argparse
import collections
import dataclasses
import re
import sys
import os
from datetime import datetime

from dotenv import load_dotenv

from source_collectors.common_crawler.argparser import parse_args
from source_collectors.common_crawler.cache import CommonCrawlerCacheManager
from source_collectors.common_crawler.crawler import CommonCrawlResult, CommonCrawlerManager
from source_collectors.common_crawler.csv_manager import CSVManager

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from util.huggingface_api_manager import HuggingFaceAPIManager
from util.miscellaneous_functions import get_filename_friendly_timestamp
from label_studio_interface.LabelStudioConfig import LabelStudioConfig
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager

"""
This module contains the main function for the Common Crawler script.
"""


@dataclasses.dataclass
class BatchInfo:
    """
    Dataclass for batch info
    """
    datetime: str
    source: str
    count: str
    keywords: str
    notes: str
    filename: str


class LabelStudioError(Exception):
    """Custom exception for Label Studio Errors"""

    pass


BATCH_HEADERS = ["Datetime", "Source", "Count", "Keywords", "Notes", "Filename"]


def get_current_time():
    """
    Returns the current time
    """
    return str(datetime.now())


def add_batch_info_to_csv(
    common_crawl_result: CommonCrawlResult, args: argparse.Namespace, last_page: int
) -> BatchInfo:
    """
    Adds batch info to CSV
    """
    batch_info = BatchInfo(
        datetime=get_current_time(),
        source="Common Crawl",
        count=str(len(common_crawl_result.url_results)),
        keywords=f"{args.url} - {args.keyword}",
        notes=f"{args.common_crawl_id}, {args.pages} pages, starting at {last_page + 1}",
        filename=f"{args.output_filename}_{get_filename_friendly_timestamp()}",
    )

    batch_info_csv_manager = CSVManager(
        file_name="batch_info", directory=args.data_dir, headers=BATCH_HEADERS
    )
    batch_info_csv_manager.add_row(dataclasses.astuple(batch_info))

    return batch_info


def main():
    """
    Main function
    """
    # Parse the arguments
    args = parse_args()

    # Initialize the Cache
    cache_manager = CommonCrawlerCacheManager(
        file_name=args.cache_filename, directory=args.data_dir
    )

    load_dotenv()

    # Initialize the HuggingFace API Manager
    hf_access_token = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
    if not hf_access_token:
        raise ValueError(
            "HUGGINGFACE_ACCESS_TOKEN not accessible in .env file in root directory. "
            "Please obtain access token from your personal account at "
            "https://huggingface.co/settings/tokens and ensure you have write access to "
            "https://huggingface.co/PDAP. Then include in .env file in root directory."
        )
    huggingface_api_manager = HuggingFaceAPIManager(
        access_token=hf_access_token, repo_id=args.huggingface_repo_id
    )
    ls_access_token = os.getenv("LABEL_STUDIO_ACCESS_TOKEN")
    if not ls_access_token:
        raise ValueError(
            "LABEL_STUDIO_ACCESS_TOKEN not accessible in .env file in root directory. "
            "Please obtain access token from your personal account at "
            "https://app.heartex.com/user/account and ensure you have read access to "
            "https://app.heartex.com/projects/61550. Then include in .env file in root directory."
        )
    ls_project_id = os.getenv("LABEL_STUDIO_PROJECT_ID")
    if not ls_project_id:
        raise ValueError(
            "LABEL_STUDIO_PROJECT_ID not accessible in .env file in root directory. "
            "Please obtain a project ID by navigating to the Label Studio project  "
            "where it will be visibile in the url. Then include in .env file in root directory."
        )

    try:
        print("Retrieving Label Studio data for deduplication")
        label_studio_results = get_ls_data()
        if label_studio_results is None:
            raise LabelStudioError("Failed to retrieve Label Studio Data")
        print("Label Studio data retrieved successfully")
    except LabelStudioError as e:
        print(e)
        raise

    if args.reset_cache:
        cache_manager.reset_cache()

    try:
        # Retrieve the last page from the cache, or 0 if it does not exist
        last_page = cache_manager.get(args.common_crawl_id, args.url, args.keyword)
        common_crawl_result = process_crawl_and_upload(
            args, last_page, huggingface_api_manager, label_studio_results
        )
    except ValueError as e:
        print(f"Error during crawling: {e}")
        return

    try:
        cache_manager.upsert(
            index=args.common_crawl_id,
            url=args.url,
            keyword=args.keyword,
            last_page=common_crawl_result.last_page_search,
        )
        cache_manager.save_cache()

    except ValueError as e:
        print(f"Error while saving cache manager: {e}")


def handle_remote_results_error(remote_results):
    """
    Handles errors in the remote results

    Args: remote_results (dict): The results from the label studio project
    Raises: LabelStudioError: If an error is found in the remote results
    """

    status_code = remote_results.get("status_code")
    if status_code == 401:
        raise LabelStudioError("Invalid Label Studio token passed! Exiting...")
    elif status_code == 404:
        raise LabelStudioError("Invalid Label Studio Project ID! Exiting...")
    else:
        raise LabelStudioError(f"Unexpected error: {remote_results}")


def validate_remote_results(remote_results):
    """
    Validates the remote results retrieved from the Label Studio project

    Args: remote_results (dict or list): The results from the Label Studio project

    Returns:
        list[dict]: If the remote results are valid
        None: If the remote results are invalid
    """
    if isinstance(remote_results, list):
        if not remote_results:
            print("No data in Label Studio project.")
            return []
        elif "url" not in remote_results[0]["data"]:
            raise LabelStudioError(
                "Column 'url' not present in Label Studio project. Exiting..."
            )
        else:
            return remote_results
    elif isinstance(remote_results, dict):
        handle_remote_results_error(remote_results)
    else:
        raise LabelStudioError("Unexpected response type.")


def get_ls_data() -> list[dict] | None:
    """Retrieves data from a Label Studio project to be used in deduplication of common crawl results.

    Returns:
        list[dict] | None: Data from the Labels Studio project or None if the result is invalid.
    """
    # Retrieve the data from the Labels Studio project
    config = LabelStudioConfig()
    api_manager = LabelStudioAPIManager(config)
    response = api_manager.export_tasks_from_project(all_tasks=True)
    remote_results = response.json()

    return validate_remote_results(remote_results)


def strip_url(url: str) -> str:
    """Strips http(s)://www. from the beginning of a url if applicable.

    Args:
        url (str): The URL to strip.

    Returns:
        str: The stripped URL.
    """
    result = re.search(r"^(?:https?://)?(?:www\.)?(.*)$", url).group(1)
    return result


def remove_local_duplicates(url_results: list[str]) -> list[str]:
    """Removes duplicate URLs from a list, ignoring http(s)://www.

    Args:
        url_results (list[str]): List of URLs to deduplicate.

    Returns:
        list[str]: List of unique URLs.
    """
    stripped_url_results = [strip_url(url) for url in url_results]
    unique_urls = collections.deque()
    adjust = 0

    for index, url in enumerate(stripped_url_results):
        if url in unique_urls:
            del url_results[index - adjust]
            adjust += 1
        else:
            unique_urls.appendleft(url)

    return url_results


def remove_remote_duplicates(
    url_results: list[str], label_studio_data: list[dict]
) -> list[str]:
    """Removes URLs from a list that are already present in the Label Studio project, ignoring http(s)://www.

    Args:
        url_results (list[str]): List of URLs to deduplicate.
        label_studio_data (list[dict]): Label Studio project data to check for duplicates.

    Returns:
        list[str]: List of remaining URLs not present in the Label Studio project.
    """
    try:
        remote_urls = [strip_url(task["data"]["url"]) for task in label_studio_data]
    except TypeError:
        print(
            "Invalid Label Studio credentials. Database could not be checked for duplicates."
        )
        return url_results
    remote_urls = set(remote_urls)

    stripped_url_results = [strip_url(url) for url in url_results]
    adjust = 0

    for index, url in enumerate(stripped_url_results):
        if url in remote_urls:
            del url_results[index - adjust]
            adjust += 1

    return url_results


def handle_csv_and_upload(
    common_crawl_result: CommonCrawlResult,
    huggingface_api_manager: HuggingFaceAPIManager,
    args: argparse.Namespace,
    last_page: int,
):
    """
    Handles the CSV file and uploads it to Hugging Face repository.
    Args:
        common_crawl_result: The result from Common Crawl.
        huggingface_api_manager: The Hugging Face API manager.
        args: The command-line arguments.
        last_page: last page crawled

    """
    batch_info = add_batch_info_to_csv(common_crawl_result, args, last_page)

    csv_manager = CSVManager(
        file_name=batch_info.filename, headers=["url"], directory=args.data_dir
    )
    csv_manager.add_rows(common_crawl_result.url_results)
    huggingface_api_manager.upload_file(
        local_file_path=csv_manager.file_path,
        repo_file_path=f"{args.output_filename}/{csv_manager.file_path.name}",
    )
    print(
        f"Uploaded file to Hugging Face repo {huggingface_api_manager.repo_id} at {args.output_filename}/{csv_manager.file_path.name}"
    )
    csv_manager.delete_file()


def process_crawl_and_upload(
    args: argparse.Namespace,
    last_page: int,
    huggingface_api_manager: HuggingFaceAPIManager,
    label_studio_data: list[dict],
) -> CommonCrawlResult:
    """
    Processes a crawl and uploads the results to Hugging Face.
    """
    # Initialize the CommonCrawlerManager
    crawler_manager = CommonCrawlerManager(args.common_crawl_id)
    # Determine the pages to search, based on the last page searched
    start_page = last_page + 1
    # Use the parsed arguments
    common_crawl_result: CommonCrawlResult = crawler_manager.crawl(
        search_term=args.url,
        keyword=args.keyword,
        num_pages=args.pages,
        start_page=start_page,
    )
    # Logic should conclude here if no results are found
    if not common_crawl_result.url_results:
        print("No url results found. Ceasing main execution.")
        add_batch_info_to_csv(common_crawl_result, args, last_page)
        return common_crawl_result

    print("Removing urls already in the database")
    common_crawl_result.url_results = remove_local_duplicates(
        common_crawl_result.url_results
    )
    common_crawl_result.url_results = remove_remote_duplicates(
        common_crawl_result.url_results, label_studio_data
    )
    if not common_crawl_result.url_results:
        print(
            "No urls not already present in the database found. Ceasing main execution."
        )
        add_batch_info_to_csv(common_crawl_result, args, last_page)
        return common_crawl_result

    handle_csv_and_upload(common_crawl_result, huggingface_api_manager, args, last_page)

    return common_crawl_result


if __name__ == "__main__":
    # Example usage: python main.py CC-MAIN-2023-50 *.gov "police"
    # Usage with optional arguments: python main.py CC-MAIN-2023-50 *.gov "police" -p 2 -o police_urls.txt
    print("Running Common Crawler...")
    main()
