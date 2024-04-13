"""
Runs integration test on Google searcher and google search queue
Requires active docker container with Postgres
"""
import dataclasses
import datetime

import psycopg
import pytest
from pytest_postgresql import factories

from google_searcher.google_search_queue_manager import GoogleSearchQueueManager
from google_searcher.google_searcher import GoogleSearcher
from tests.database.ProdSchemaManager import ProdSchemaManager
from util.db_manager import DBManager

"""
This requires a postgresql docker container set up and listening on port 5432"
The setup should mirror what is in start_database_setup.sh
"""

FAKE_SEARCH_ROW_COUNT = 10

prod_schema_manager = ProdSchemaManager()
postgresql_in_docker = factories.postgresql_noproc(
    port="5432",
    user="myuser",
    password="mypassword",
    host="host.docker.internal",
    load=[prod_schema_manager.schema_path]
)
postgresql = factories.postgresql("postgresql_in_docker")

@dataclasses.dataclass
class BatchQuerySet:
    """
    Class representing a batch of search queries.

    Attributes:
        short_name (str): The short name of the batch.
        description (str): The description of the batch.
        search_queries (list[str]): The list of search queries in the batch.
    """
    short_name: str
    description: str
    search_queries: list[str]


DOG_BATCH_QUERY_SET = BatchQuerySet(
    short_name="Dog questions",
    description="Questions of and relating to the nature of dogs",
    search_queries=["Why does dog look at me so"]
)

FISHDOG_BATCH_QUERY_SET = BatchQuerySet(
    short_name="Fish-Dog Questions",
    description="Questions of and relating to the nature of fish that act like dogs",
    search_queries=[
        "Can I take my fish to the dog park if it acts like a dog",
        "Can you teach a fish how to sit"
    ]
)


@pytest.fixture
def google_searcher_mock(mocker):
    """
    A partially-mocked Google Searcher which mocks the calls to the Google Search API
    Args:
        mocker:

    Returns:

    """
    api_key = "test_api_key"
    cse_id = "test_cse_id"
    mock_service = mocker.patch("google_searcher.google_searcher.build")

    # Create a mock for the Google API service object and set it as the return_value for the 'build' method
    mock_google_api_service = mocker.Mock()
    mock_service.return_value = mock_google_api_service
    gs = GoogleSearcher(api_key, cse_id)

    # Replace call_google_search with method to validate expected query and return fake search data
    mocker.patch.object(gs, 'call_google_search', new=validate_google_search_call_and_return_fake_search_data)
    return gs


def insert_queue_data(db: psycopg.Connection):
    """
    Inserts data into the search_batch_info and search_queue tables in the specified database.

    Args:
        db: A psycopg2 connection to the database where the data will be inserted.
    """
    cur = db.cursor()
    # Begin by inserting into batch
    batch_insert_sql = """
    INSERT INTO search_batch_info(short_name, description)
    Values (%s, %s)
    """
    cur.execute(batch_insert_sql, (DOG_BATCH_QUERY_SET.short_name, DOG_BATCH_QUERY_SET.description))
    cur.execute(batch_insert_sql, (FISHDOG_BATCH_QUERY_SET.short_name, FISHDOG_BATCH_QUERY_SET.description))

    sql_script = """
    INSERT INTO search_queue (batch_id, search_query)
    VALUES (%s, %s);
    """
    cur.execute(sql_script, (1, DOG_BATCH_QUERY_SET.search_queries[0]))
    cur.execute(sql_script, (2, FISHDOG_BATCH_QUERY_SET.search_queries[0]))
    cur.execute(sql_script, (2, FISHDOG_BATCH_QUERY_SET.search_queries[1]))
    db.commit()


def get_fake_search_data(tag: str) -> dict:
    """
    Retrieve fake search data based on a given tag.

    Args:
        tag (str): The tag to be included in the snippet.

    Returns:
        dict: A dictionary containing fake search data.

    """
    fake_search_data = {'items': []}
    for i in range(1, FAKE_SEARCH_ROW_COUNT + 1):
        number = i
        # ASCII value of 'a' is 97, so we add i - 1 to it to get the incremental letter
        letter = chr(97 + (i - 1) % 26)  # Use modulo 26 to loop back to 'a' after 'z'
        fake_search_data['items'].append(
            {
                'link': f'https://www.example.com/{number}',
                'title': 'Example Title',
                'snippet': f'This {tag} snippet contains the letter {letter}'
            }
        )
    return fake_search_data


def validate_google_search_call_and_return_fake_search_data(query):
    """
    Args:
        query: The search query to validate against the available batch query set.

    Returns:
        Fake search data matching the query if the query is valid.

    Raises:
        AssertionError: If the query is not valid or does not match the expected batch query set.
    """
    if "dog" in query and "fish" not in query:
        assert query in DOG_BATCH_QUERY_SET.search_queries
        return get_fake_search_data("dog")
    if "fish" in query:
        assert query in FISHDOG_BATCH_QUERY_SET.search_queries
        return get_fake_search_data("fish")
    assert False


def validate_search_results(tag: str, start: int, end: int, cur: psycopg.cursor):
    """
    Validates the search results for a given tag, start, end, and cursor.

    Args:
        tag (str): The search tag.
        start (int): The starting value for the search ID.
        end (int): The ending value for the search ID.
        cur (psycopg.cursor): The PostgreSQL cursor object.

    """
    # Test that expected data is in SEARCH_RESULTS table for first batch
    fetch_sql_script = """
    SELECT 
        RESULT_ID,
        SEARCH_ID,
        URL,
        TITLE,
        SNIPPET 
    FROM SEARCH_RESULTS
    WHERE SEARCH_ID >= %s and SEARCH_ID <= %s
    """
    cur.execute(fetch_sql_script, (start, end))
    results = cur.fetchall()
    fake_query_results = get_fake_search_data(tag)
    for idx, result in enumerate(results[start - 1:end]):
        result_data = fake_query_results['items'][idx]
        assert result == (idx + 1, 1, result_data['link'], result_data['title'], result_data['snippet'])


def validate_search_queue(search_id: int, batch_id: int, search_query: str, cur):
    """
    Args:
        search_id (int): The ID of the search.
        batch_id (int): The ID of the batch.
        search_query (str): The query string for the search.
        cur: The database cursor object.

    Raises:
        AssertionError: If the expected data is not found in the SEARCH_QUEUE table.

    """
    # Test that expected data is in SEARCH_QUEUE table
    fetch_sql_script = """
    SELECT 
        SEARCH_ID,
        BATCH_ID,
        SEARCH_QUERY,
        EXECUTED_DATETIME 
    FROM SEARCH_QUEUE
    WHERE SEARCH_ID = %s and BATCH_ID = %s and SEARCH_QUERY = %s
    """
    cur.execute(fetch_sql_script, (search_id, batch_id, search_query))
    results = cur.fetchall()
    assert results[0][0:3] == (search_id, batch_id, search_query)
    assert isinstance(results[0][3], datetime.datetime)


def test_queue_manager_integration(postgresql, google_searcher_mock, mocker):
    """
    Performs an integration test on the expected functionality of the queue manager

    Args:
        postgresql: The PostgreSQL database connection object.
        google_searcher_mock: The mock object for the `GoogleSearcher` class.
        mocker: The pytest mocker object.

    """
    # Insert Queue Data into database
    insert_queue_data(postgresql)

    # Load partially-mocked queue manager
    mocker.patch('psycopg.connect', return_value=postgresql)
    queue_manager = GoogleSearchQueueManager(
        google_searcher=google_searcher_mock,
        database_manager=DBManager(*(0, 0, 0, 0, 0)),
    )

    # Run queue manager
    queue_manager.run_searches_until_quota_exceeded()

    # Validate presence of expected data in both search queue and search results
    cur = postgresql.cursor()
    try:
        validate_search_queue(
            search_id=1,
            batch_id=1,
            search_query=DOG_BATCH_QUERY_SET.search_queries[0],
            cur=cur
        )
        validate_search_queue(
            search_id=2,
            batch_id=2,
            search_query=FISHDOG_BATCH_QUERY_SET.search_queries[0],
            cur=cur
        )
        validate_search_queue(
            search_id=3,
            batch_id=2,
            search_query=FISHDOG_BATCH_QUERY_SET.search_queries[1],
            cur=cur
        )

        validate_search_results(
            tag="dog",
            start=1,
            end=10,
            cur=cur
        )
        validate_search_results(
            tag="fish",
            start=11,
            end=30,
            cur=cur
        )
    except Exception as e:
        raise e
