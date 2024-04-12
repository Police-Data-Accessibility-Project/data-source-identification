# Agency Homepage Searcher

### Single sentence summary

This module uses google searches to fill in missing homepage data for agencies in the PDAP database.

### Somewhat longer summary

This module is designed to do the following:
1. Take existing data from the `AGENCIES` table in the PDAP PostgreSQL database
2. Identify those agencies which lack a homepage
3. Perform [automated google searches](https://developers.google.com/custom-search/v1/overview) for potential homepages for the agency, using information from the database row
4. Upload those automated searches to the PDAP Huggingface database at [PDAP/possible_homepage_urls](https://huggingface.co/datasets/PDAP/possible_homepage_urls)
5. And update the AGENCY_URL_SEARCH_CACHE in the PDAP PostgreSQL database to ensure those rows in the `AGENCIES` table already searched for are not searched for again

## Environment Setup

This script requires a number of environment variables to be provided in an associated `.env` file in the root directory in order to function correctly:

* CUSTOM_SEARCH_API_KEY - The API key required for accessing the [Google Custom Search Engine](https://developers.google.com/custom-search/v1/overview). Obtainable by clicking the "Get a Key" button in the linked overview, and associating it with an existing custom search engine or one that you create.
* CUSTOM_SEARCH_ENGINE_ID - The CSE (Custom Search Engine) ID required for identifying the specific search engine to use. Accessible by clicking on the search engine in the [Programmable Search Engine control panel](https://programmablesearchengine.google.com/controlpanel/all).
* DIGITAL_OCEAN_DB_USERNAME - The username to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_PASSWORD - The password to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_HOST - The host to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_PORT - The port to be used for logging into the PostgreSQL database
* DIGITAL_OCEAN_DB_NAME - The database name to be used for logging into the PostgreSQL database
* HUGGINGFACE_ACCESS_TOKEN - An access token for a user with permissions to upload data to the [PDAP/possible_homepage_urls](https://huggingface.co/datasets/PDAP/possible_homepage_urls) dataset

## Running script



## Running tests

TODO: Include notes on running integration test with database
