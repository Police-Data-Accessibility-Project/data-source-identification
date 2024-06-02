# Common Crawler

This module interfaces with the Common Crawl dataset to extract urls.

## Installation

Python Version Required: 3.11

To install all necessary dependencies, run the following command from the root directory:

```bash
pip install -r requirements.txt
```


## Usage Example

### Environment Requirements

Please ensure you have a `.env` file located in the root directory (not the `common_crawler` directory) 
which contains the following environment variable:
* HUGGINGFACE_ACCESS_TOKEN = The access token to enable writing to the associated PDAP dataset.
To obtain your access token, consult user settings at https://huggingface.co/settings/tokens 
and ensure you have write access to https://huggingface.co/PDAP .

To check for duplicate urls against a Label Studio project, add the following environment variables:

* LABEL_STUDIO_ACCESS_TOKEN = The access token for the Label Studio API. This can be
  obtained by logging into Label Studio and navigating to the [user account section](https://app.heartex.com/user/account), where the access token can be copied.
* LABEL_STUDIO_PROJECT_ID = The project ID for the Label Studio API. This can be
  obtained by logging into Label Studio and navigating to the relevant project, where the project id will be in the URL.
* LABEL_STUDIO_ORGANIZATION_ID = The organization ID for the Label Studio API. This can
  be obtained by logging into Label Studio and navigating to the [Organization section](https://app.heartex.com/organization?page=1), where the organization ID can be copied.

### Instructions

Run the following script from the root directory
```bash
python common_crawler/main.py CC-MAIN-2023-50 '*.gov' police --config common_crawler/config.ini --pages 2
```

This example will crawl a single page (typically 15000 records) of the Common Crawl dataset with ID `CC-MAIN-2023-50` 
and search for the term `police` in all the pages with the `.gov` domain. It will use the default configuration file `config.ini`
to determine the json cache location and the location of the output csv file. 

Note that the cache records the most recent page number that was used for given combination of Common Crawl ID, url search term, and keyword. 
If the same command is run again, it will start from the next page.
If you want to reset the cache, you can use the `--reset-cache` flag.

By default, the output csv file will be named `urls.csv` and will be located in the `data`  directory of the module.
This csv file contains both the url and the parameters used to query it.

### Parameters

- **common_crawl_id**: Required. Specifies the Common Crawl Index to perform the search on.
- **url**: Required. Specifies the domain URL to query. Wildcard characters such as * can be used to expand the search. Note that the query must be contained within quotes (as in '*.gov') to prevent misinterpretation of wildcards
- **search_term**: Required. Specifies keyword within the url to search for.
- **-c or --config**: Optional. Specifies the configuration file to use. The default value is config.ini.
- **-p or --pages**: Optional. Specifies the number of pages to search. The default value is 1.
- **--reset-cache**: Optional. If set, it resets the cache before starting the crawl.

### Configuration

Several attributes are currently defined in `config.ini`:
- **cache_filename**: This is the name of the cache file. The default value is `cache`. The file will be saved with a `.json` extension.
- **output_filename**: This is the name of the output file. The default value is `urls`. The file will be saved with a `.csv` extension.
- **data_dir**: This is the directory where the cache and output files will be saved. The default value is `data`.
- **huggingface_repo_id**: This is the repository ID for the hugging face dataset which urls will be uploaded to

## Code Structure 

The code is structured as follows:
- **main.py**: This is the main file that is used to run the module. It contains the logic to parse the command line arguments and call the necessary functions.
- **crawler.py**: This file contains the logic to interface with the Common Crawl dataset and extract urls.
- **cache.py**: This file contains the logic to read and write the cache file.
- **argparser.py**: This file contains the logic to parse the command line and config arguments.
- **csv_manager.py**: This file contains the logic to write the output csv file.
- **utils.py**: This file contains utility functions.
- **config.ini**: This file contains the default configuration values.
- **README.md**: This file contains the documentation for the module. You're reading it right now. Isn't that nifty!

## Testing

A suite of unit and integration tests were developed for this module.

To run the tests, run the following command from this directory:

```bash
pytest ../tests/test_common_crawler_integration.py
pytest ../tests/test_common_crawler_unit.py
```