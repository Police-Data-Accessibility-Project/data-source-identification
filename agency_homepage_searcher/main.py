import sys
import os

from dotenv import load_dotenv

# The below code sets the working directory to be the root of the entire repository
# This is done to solve otherwise quite annoying import issues.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agency_homepage_searcher.google_searcher import GoogleSearcher
from agency_homepage_searcher.homepage_searcher import HomepageSearcher
from util.db_manager import DBManager
from util.huggingface_api_manager import HuggingFaceAPIManager

if __name__ == "__main__":
    # Load the custom search API key and CSE ID from the .env file
    load_dotenv()
    google_searcher = GoogleSearcher(
        api_key=os.getenv("CUSTOM_SEARCH_API_KEY"),
        cse_id=os.getenv("CUSTOM_SEARCH_ENGINE_ID"))
    db_manager = DBManager(
        database_url=os.getenv("DO_DATABASE_URL")
    )
    huggingface_api_manager = HuggingFaceAPIManager(
        access_token=os.getenv("HUGGINGFACE_ACCESS_TOKEN"),
        repo_id="PDAP/possible_homepage_urls"
    )
    homepage_searcher = HomepageSearcher(
        search_engine=google_searcher,
        database_manager=db_manager,
        huggingface_api_manager=huggingface_api_manager
    )
    homepage_searcher.search_and_upload(
        max_searches=100
    )
