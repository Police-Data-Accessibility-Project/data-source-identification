import os
import sys

from dotenv import load_dotenv

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_searcher.google_search_queue_manager import GoogleSearchQueueManager
from google_searcher.google_searcher import GoogleSearcher
from util.db_manager import DBManager

if __name__ == "__main__":
    # Load the custom search API key and CSE ID from the .env file
    load_dotenv()
    google_searcher = GoogleSearcher(
        api_key=os.getenv("CUSTOM_SEARCH_API_KEY"),
        cse_id=os.getenv("CUSTOM_SEARCH_ENGINE_ID"))
    # TODO: Change to call API. Or consider a non-API method entirely.
    # TODO: Perhaps a separate database?
    db_manager = DBManager(
        user=os.getenv("DIGITAL_OCEAN_DB_USERNAME"),
        password=os.getenv("DIGITAL_OCEAN_DB_PASSWORD"),
        host=os.getenv("DIGITAL_OCEAN_DB_HOST"),
        port=os.getenv("DIGITAL_OCEAN_DB_PORT"),
        db_name=os.getenv("DIGITAL_OCEAN_DB_NAME")
    )
    queue_manager = GoogleSearchQueueManager(
        database_manager=db_manager,
        google_searcher=google_searcher
    )
    queue_manager.run_searches_until_quota_exceeded()