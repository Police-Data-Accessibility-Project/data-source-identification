from common_crawler.argparser import parse_args
from common_crawler.cache import CacheStorage, CommonCrawlerCacheManager
from common_crawler.crawler import CommonCrawlerManager
from common_crawler.csv_manager import CSVManager
from common_crawler.utils import UrlResults

"""
This module contains the main function for the Common Crawler script.
"""


def main():
    # Parse the arguments
    args = parse_args()

    # Initialize the Cache
    cache_manager = CommonCrawlerCacheManager(
        storage=CacheStorage(
            file_name=args.cache_filename,
            directory=args.data_dir
        )
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
        results = manager.crawl(args.common_crawl_id, args.url, args.search_term, args.pages)

        if results:
            csv_manager.add_rows(results)
        else:
            print("No results found.")

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
