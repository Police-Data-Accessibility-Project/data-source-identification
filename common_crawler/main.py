import argparse
import dataclasses
import sys
import os
from datetime import datetime

from dotenv import load_dotenv

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util.huggingface_api_manager import HuggingFaceAPIManager
from util.miscellaneous_functions import get_filename_friendly_timestamp
from common_crawler.argparser import parse_args
from common_crawler.cache import CommonCrawlerCacheManager
from common_crawler.crawler import CommonCrawlerManager, CommonCrawlResult
from common_crawler.csv_manager import CSVManager

"""
This module contains the main function for the Common Crawler script.
"""


@dataclasses.dataclass
class BatchInfo:
    datetime: str
    source: str
    count: str
    keywords: str
    notes: str


BATCH_HEADERS = ['Datetime', 'Source', 'Count', 'Keywords', 'Notes']


def get_current_time():
    return str(datetime.now())


def add_batch_info_to_csv(batch_info: BatchInfo, data_dir: str):
    batch_info_csv_manager = CSVManager(
        file_name='batch_info',
        directory=data_dir,
        headers=BATCH_HEADERS
    )
    batch_info_csv_manager.add_row(dataclasses.astuple(batch_info))


def main():
    # Parse the arguments
    args = parse_args()

    # Initialize the Cache
    cache_manager = CommonCrawlerCacheManager(
        file_name=args.cache_filename,
        directory=args.data_dir
    )

    load_dotenv()
    # Initialize the HuggingFace API Manager
    hf_access_token = os.getenv("HUGGINGFACE_ACCESS_TOKEN")
    if not hf_access_token:
        raise ValueError(
            "HUGGINGFACE_ACCESS_TOKEN not accessible in .env file in root directory. "
            "Please obtain access token from your personal account at "
            "https://huggingface.co/settings/tokens and ensure you have write access to "
            "https://huggingface.co/PDAP. Then include in .env file in root directory.")
    huggingface_api_manager = HuggingFaceAPIManager(
        access_token=hf_access_token,
        repo_id=args.huggingface_repo_id
    )

    if args.reset_cache:
        cache_manager.reset_cache()

    try:
        # Retrieve the last page from the cache, or 0 if it does not exist
        last_page = cache_manager.get(args.common_crawl_id, args.url, args.keyword)
        common_crawl_result = process_crawl_and_upload(args, last_page, huggingface_api_manager)
        batch_info = BatchInfo(
            datetime=get_current_time(),
            source="Common Crawl",
            count=str(len(common_crawl_result.url_results)),
            keywords=f"{args.url} - {args.keyword}",
            notes=args.common_crawl_id
        )
        add_batch_info_to_csv(batch_info, args.data_dir)
    except ValueError as e:
        print(f"Error during crawling: {e}")
        return

    try:
        cache_manager.upsert(
            index=args.common_crawl_id,
            url=args.url,
            keyword=args.keyword,
            last_page=common_crawl_result.last_page_search)
        cache_manager.save_cache()
    except ValueError as e:
        print(f"Error while saving cache manager: {e}")


def handle_csv_and_upload(
        common_crawl_result: CommonCrawlResult,
        huggingface_api_manager: HuggingFaceAPIManager,
        args: argparse.Namespace):
    """
    Handles the CSV file and uploads it to Hugging Face repository.
    Args:
        common_crawl_result: The result from Common Crawl.
        huggingface_api_manager: The Hugging Face API manager.
        args: The command-line arguments.

    """
    csv_manager = CSVManager(
        file_name=f"{args.output_filename}_{get_filename_friendly_timestamp()}",
        headers=['url'],
        directory=args.data_dir
    )
    csv_manager.add_rows(common_crawl_result.url_results)
    huggingface_api_manager.upload_file(
        local_file_path=csv_manager.file_path,
        repo_file_path=f"{args.output_filename}/{csv_manager.file_path.name}"
    )
    print(
        f"Uploaded file to Hugging Face repo {huggingface_api_manager.repo_id} at {args.output_filename}/{csv_manager.file_path.name}")
    csv_manager.delete_file()


def process_crawl_and_upload(
        args: argparse.Namespace,
        last_page: int,
        huggingface_api_manager: HuggingFaceAPIManager) -> CommonCrawlResult:
    # Initialize the CommonCrawlerManager
    crawler_manager = CommonCrawlerManager(
        args.common_crawl_id
    )
    # Determine the pages to search, based on the last page searched
    start_page = last_page + 1
    # Use the parsed arguments
    common_crawl_result: CommonCrawlResult = crawler_manager.crawl(
        search_term=args.url,
        keyword=args.keyword,
        num_pages=args.pages,
        start_page=start_page
    )
    # Logic should conclude here if no results are found
    if not common_crawl_result.url_results:
        print("No url results found. Ceasing main execution.")
        return common_crawl_result
    handle_csv_and_upload(common_crawl_result, huggingface_api_manager, args)
    return common_crawl_result


if __name__ == "__main__":
    # Example usage: python main.py CC-MAIN-2023-50 *.gov "police"
    # Usage with optional arguments: python main.py CC-MAIN-2023-50 *.gov "police" -p 2 -o police_urls.txt
    print("Running Common Crawler...")
    main()
