# Google Searcher

### Single sentence summary

This module runs daily a sequence of searches from a database queue and uploads the results back into the queue.

### Somewhat longer summary

This module is designed to do the following:
1. Load queued searches from the `search_queue` table in the PDAP PostgreSQL database
2. Run [automated google searches](https://developers.google.com/custom-search/v1/overview) for as many results as possible until the search quota is exceeded (100 a day unless more are paid for)
3. Upload the results to the `search_results` table in the PDAP PostgreSQL database.

## Environment Setup

This script requires a number of environment variables to be provided in an associated `.env` file in the root directory in order to function correctly:

* CUSTOM_SEARCH_API_KEY - The API key required for accessing the [Google Custom Search Engine](https://developers.google.com/custom-search/v1/overview.)
* CUSTOM_SEARCH_ENGINE_ID - The CSE (Custom Search Engine) ID required for identifying the specific search engine to use.
* DIGITAL_OCEAN_DB_USERNAME - The username to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_PASSWORD - The password to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_HOST - The host to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_PORT - The port to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_NAME - The database name to be used for logging into the PostgreSQL database

# One Time Scripts

The `one_time_scripts` folder is used to store all python scripts which generate values to be added to the queue. As the name implies, they are only intended to be run once, or at least manually, to generate scripts to be added to the queue.

# Running Scripts

This should be as simple as running `python main.py` while within the directory. 