The Auto-Googler is a tool that automates the process of fetching URLs from Google Search and processing them for source collection.

Auto-Googler logic consists of:

1. `GoogleSearcher`, the class that interfaces with the Google Search API.
2. `AutoGoogler`, the class that orchestrates the search process.
3. `SearchConfig`, the class that holds the configuration for the search queries.

The following environment variables must be set in an `.env` file in the root directory:

- GOOGLE_API_KEY: The API key required for accessing the Google Custom Search API.

The Auto-Googler is intended to be used in conjunction with the other tools in this repo.
