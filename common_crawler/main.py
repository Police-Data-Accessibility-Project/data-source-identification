from common_crawler.argparser import parse_args
from common_crawler.crawler import CommonCrawlerManager

"""
This module contains the main function for the Common Crawler script.
"""

def main():
    # Parse the arguments
    args = parse_args()

    # Initialize the CommonCrawlerManager
    manager = CommonCrawlerManager()

    if args.reset_cache:
        manager.reset_cache()

    try:
        # Use the parsed arguments
        results = manager.crawl(args.common_crawl_id, args.url, args.search_term, args.pages)

        # Process the results
        if results:
            if args.output:
                # If an output file is specified, write the URLs to the file
                with open(args.output, 'w') as f:
                    for result in results:
                        f.write(result + '\n')
                print(f"URLs written to {args.output}")
            else:
                # If no output file is specified, print the URLs to the console
                print("Found URLs:")
                for result in results:
                    print(result)
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
    main()
