# Agency Identifier

Attempts to match links with an agency from the PDAP database

## How to use

1. Clone the repository
2. Create a CSV or text file containing a list of urls to be identified, one per line
3. Download the agency CSV from [Airtable](https://airtable.com/app473MWXVJVaD7Es/shr43ihbyM8DDkKx4/tblpnd3ei5SlibcCX) and place it in the same directory
4. Run `python3 identifier.py [url_file]`

## Requirements

- `Python 3`
- `requests`
- `dotenv`
- `tqdm`
