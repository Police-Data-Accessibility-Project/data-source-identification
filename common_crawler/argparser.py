import argparse

"""
This module contains the argument parser for command line arguments
for the Common Crawler script.
"""

def parse_args() -> argparse.Namespace:
    """
    Parse the command line arguments for the Common Crawler script.
    Returns: The parsed arguments

    """
    parser = argparse.ArgumentParser(
        description='Query the Common Crawl dataset and optionally save the results to a file.')
    # Add the required arguments
    parser.add_argument('common_crawl_id', type=str, help='The Common Crawl ID')
    parser.add_argument('url', type=str, help='The URL to query')
    parser.add_argument('search_term', type=str, help='The search term')
    # Optional arguments for the number of pages and the output file, and a flag to reset the cache
    parser.add_argument('-p', '--pages', type=int, default=1, help='The number of pages to search (default: 1)')
    parser.add_argument('-o', '--output', type=str, help='The name of the output text file for the URLs (optional)')
    parser.add_argument('--reset-cache', action='store_true', help='Reset the cache before starting the crawl')
    # Parse the arguments
    args = parser.parse_args()

    return args
