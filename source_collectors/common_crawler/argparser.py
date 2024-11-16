import argparse
import configparser
import re

"""
This module contains the argument parser for command line arguments
for the Common Crawler script.
"""


def valid_common_crawl_id(common_crawl_id: str) -> bool:
    """
    Validate the Common Crawl ID format.
    The Common Crawl ID should be in the format CC-MAIN-YYYY-WW.
    Args:
        common_crawl_id: The Common Crawl ID to validate
    Returns:
        True if the Common Crawl ID is valid, False otherwise
    """
    return re.match(r"CC-MAIN-\d{4}-\d{2}", common_crawl_id) is not None


def parse_args() -> argparse.Namespace:
    """
    Parse the command line arguments for the Common Crawler script
    as well as the configuration file.
    Arguments parsed include:
    - The Common Crawl ID
    - The URL to query
    - The search term
    - The number of pages to search
    - The configuration file (defaults to config.ini)
    - A flag to reset the cache
    Returns: The parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Query the Common Crawl dataset and optionally save the results to a file."
    )
    # Add the required arguments
    parser.add_argument("common_crawl_id", type=str, help="The Common Crawl ID")
    parser.add_argument("url", type=str, help="The URL to query")
    parser.add_argument("keyword", type=str, help="The keyword to search in the url")
    # Optional arguments for the number of pages and the output file, and a flag to reset the cache
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.ini",
        help="The configuration file to use",
    )
    parser.add_argument(
        "-p",
        "--pages",
        type=int,
        default=1,
        help="The number of pages to search (default: 1)",
    )
    parser.add_argument(
        "--reset-cache",
        action="store_true",
        default=False,
        help="Reset the cache before starting the crawl",
    )

    args = parser.parse_args()

    # Validate the Common Crawl ID format
    if not valid_common_crawl_id(args.common_crawl_id):
        parser.error(
            "Invalid Common Crawl ID format. Expected format is CC-MAIN-YYYY-WW."
        )

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(args.config)

    # Combine parsed arguments with configuration file defaults
    app_parser = argparse.ArgumentParser(parents=[parser], add_help=False)
    app_parser.set_defaults(**config["DEFAULT"])

    app_args = app_parser.parse_args()

    # Print arguments
    print(f"--Common Crawl ID: {app_args.common_crawl_id}")
    print(f"--URL: {app_args.url}")
    print(f"--Keyword: {app_args.keyword}")
    print(f"--Number of Pages: {app_args.pages}")
    print(f"--Configuration File: {app_args.config}")
    print(f"--Reset Cache: {app_args.reset_cache}")
    print(f"--Output File: {app_args.output_filename}.csv")
    print(f"--Cache File: {app_args.cache_filename}.json")
    print(f"--Data Directory: {app_args.data_dir}")

    return app_args
