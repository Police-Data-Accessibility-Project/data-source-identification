# Agency Identifier

The Agency Identifier is a Python application that matches URLs with an agency from the PDAP database. It takes a list of URLs as input, either from a CSV file or a DataFrame, and returns a DataFrame with the matched agencies.

## How to use

### Running from the command line

1. Clone the repository.
2. Create a CSV file containing a list of URLs to be identified. The URLs should be listed one per line, and the file should have at least a "url" column.
3. Run the command `python3 identifier.py [url_file]`, replacing `[url_file]` with the path to your CSV file.
4. The results will be written to a file named `results.csv` in the same directory.

### Using the "identifier_main" function

If you're using the Agency Identifier in your own Python code, you can import the `process_and_write_data` function. This function takes a DataFrame as an argument and returns a DataFrame with the matched agencies.

Here's an example of how to use it:

```python
import polar as pl
from identifier import process_and_write_data

# Create a DataFrame with the URLs to be identified
df = pl.DataFrame({"url": ["http://agency1.com/page1", "http://agency2.com/page2"]})

# Call the identifier_main function
result = process_and_write_data(df)

# Print the resulting DataFrame
print(result)
```

# Requirements

- Python 3
- urllib
- re
- polars
- requests