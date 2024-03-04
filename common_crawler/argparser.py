import argparse
import configparser

"""
This module contains the argument parser for command line arguments
for the Common Crawler script.
"""

def parse_args() -> argparse.Namespace:
    """
    Parse the command line arguments for the Common Crawler script.
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
        description='Query the Common Crawl dataset and optionally save the results to a file.')
    # Add the required arguments
    parser.add_argument('common_crawl_id', type=str, help='The Common Crawl ID')
    parser.add_argument('url', type=str, help='The URL to query')
    parser.add_argument('search_term', type=str, help='The search term')
    # Optional arguments for the number of pages and the output file, and a flag to reset the cache
    parser.add_argument('-c', '--config', type=str, default='config.ini', help='The configuration file to use')
    parser.add_argument('-p', '--pages', type=int, default=1, help='The number of pages to search (default: 1)')
    parser.add_argument('--reset-cache', action='store_true', default=False, help='Reset the cache before starting the crawl')
    # Parse the arguments

    # Add config file to args
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(args.config)

    app_parser = argparse.ArgumentParser(parents=[parser], add_help=False)
    app_parser.set_defaults(**config['DEFAULT'])

    app_args = app_parser.parse_args()

    # Print arguments
    print(f"--Common Crawl ID: {app_args.common_crawl_id}")
    print(f"--URL: {app_args.url}")
    print(f"--Search Term: {app_args.search_term}")
    print(f"--Number of Pages: {app_args.pages}")
    print(f"--Configuration File: {app_args.config}")
    print(f"--Reset Cache: {app_args.reset_cache}")
    print(f"--Output File: {app_args.output_filename}.csv")
    print(f"--Cache File: {app_args.cache_filename}.json")
    print(f"--Data Directory: {app_args.data_dir}")

    return app_args
