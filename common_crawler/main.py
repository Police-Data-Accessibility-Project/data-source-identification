import sys
import os

from dotenv import load_dotenv

from util.huggingface_api_manager import HuggingFaceAPIManager

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common_crawler.argparser import parse_args
from common_crawler.cache import CommonCrawlerCacheManager
from common_crawler.crawler import CommonCrawlerManager, CommonCrawlResult
from common_crawler.csv_manager import CSVManager

"""
This module contains the main function for the Common Crawler script.
"""


def main():
    # Parse the arguments
    args = parse_args()

    # Initialize the Cache
    cache_manager = CommonCrawlerCacheManager(
        file_name=args.cache_filename,
        directory=args.data_dir
    )

    # Initialize the CSV Manager
    csv_manager = CSVManager(
        file_name=args.output_filename,
        directory=args.data_dir
    )

    load_dotenv()
    # Initialize the HuggingFace API Manager
    huggingface_api_manager = HuggingFaceAPIManager(
        access_token=os.getenv("HUGGINGFACE_ACCESS_TOKEN"),
        repo_id=args.huggingface_repo_id
    )

    if args.reset_cache:
        cache_manager.reset_cache()
        csv_manager.initialize_file()

    try:
        # Initialize the CommonCrawlerManager
        crawler_manager = CommonCrawlerManager(
            args.common_crawl_id
        )
        # Retrieve the last page from the cache, or 0 if it does not exist
        last_page = cache_manager.get(args.common_crawl_id, args.url, args.keyword)
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
            return

        csv_manager.add_rows(common_crawl_result.url_results)
        cache_manager.upsert(
            index=args.common_crawl_id,
            url=args.url,
            keyword=args.keyword,
            last_page=common_crawl_result.last_page_search)
        cache_manager.save_cache()


    except ValueError as e:
        print(f"Error during crawling: {e}")
    except Exception as e:
        # Catch-all for any other errors
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Example usage: python main.py CC-MAIN-2023-50 *.gov "police"
    # Usage with optional arguments: python main.py CC-MAIN-2023-50 *.gov "police" -p 2 -o police_urls.txt
    print("Running Common Crawler...")
    main()
