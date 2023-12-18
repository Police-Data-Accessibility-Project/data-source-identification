# Agency Identifier

Attempts to match links with an agency from the PDAP database

## How to use

1. Clone the repository
2. If running from the command line, create a CSV containing a list of urls to be identified, one per line with at least a "url" column
3. Run `python3 identifier.py [url_file]`
4. Results will be written in the same directory as results.csv
5. If importing "identifier_main" function, it expects a dataframe as an argument and returns a resulting dataframe

## Requirements

- `Python 3`
- `requests`
- `dotenv`
- `tqdm`
- `polars`