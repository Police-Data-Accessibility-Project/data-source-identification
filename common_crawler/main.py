import sys
import os

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common_crawler.argparser import parse_args
from common_crawler.cache import CommonCrawlerCache
from common_crawler.crawler import CommonCrawlerManager, CommonCrawlResult
from common_crawler.csv_manager import CSVManager

"""
This module contains the main function for the Common Crawler script.
"""


def main():
    # Parse the arguments
    args = parse_args()

    # Initialize the Cache
    cache_manager = CommonCrawlerCache(
        file_name=args.cache_filename,
        directory=args.data_dir
    )

    # Initialize the CSV Manager
    csv_manager = CSVManager(
        file_name=args.output_filename,
        directory=args.data_dir
    )

    if args.reset_cache:
        cache_manager.reset_cache()
        csv_manager.initialize_file()

    try:
        # Initialize the CommonCrawlerManager
        manager = CommonCrawlerManager(
            cache_manager=cache_manager
        )

        # Use the parsed arguments
        common_crawl_result: CommonCrawlResult = manager.crawl(args.common_crawl_id, args.url, args.keyword, args.pages)

        if common_crawl_result.url_results:
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
