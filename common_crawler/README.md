# Common Crawler

This module interfaces with the Common Crawl dataset to extract urls.

### Installation

To install all necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### Usage Example

```bash
python main.py CC-MAIN-2023-50 *.gov police
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

- **common_crawl_id**: This is a required argument. It specifies the Common Crawl ID.
- **url**: This is a required argument. It specifies the URL to query.
- **search_term**: This is a required argument. It specifies the search term.
- **-c or --config**: This is an optional argument. It specifies the configuration file to use. The default value is config.ini.
- **-p or --pages**: This is an optional argument. It specifies the number of pages to search. The default value is 1.
- **--reset-cache**: This is an optional argument. If set, it resets the cache before starting the crawl.

### Configuration

Several attributes are currently defined in `config.ini`:
- **cache_filename**: This is the name of the cache file. The default value is `cache`. The file will be saved with a `.json` extension.
- **output_filename**: This is the name of the output file. The default value is `urls`. The file will be saved with a `.csv` extension.
- **data_dir**: This is the directory where the cache and output files will be saved. The default value is `data`.

### Code Structure 

The code is structured as follows:
- **main.py**: This is the main file that is used to run the module. It contains the logic to parse the command line arguments and call the necessary functions.
- **crawler.py**: This file contains the logic to interface with the Common Crawl dataset and extract urls.
- **cache.py**: This file contains the logic to read and write the cache file.
- **argparser.py**: This file contains the logic to parse the command line and config arguments.
- **csv_manager.py**: This file contains the logic to write the output csv file.
- **utils.py**: This file contains utility functions.
- **config.ini**: This file contains the default configuration values.
- **requirements.txt**: This file contains the necessary dependencies for the module.
- **README.md**: This file contains the documentation for the module. You're reading it right now. Isn't that nifty!