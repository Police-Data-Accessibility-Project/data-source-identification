import json
import os
from dataclasses import asdict
from dotenv import load_dotenv

from openai import OpenAI

from data_request.florida_data_request.request_dataclasses import SearchResult, MostRelevantResult
from data_request.florida_data_request.request_db_manager import table_exists, create_relevant_search_gpt_table, \
    get_next_query_and_results, upload_most_relevant_result


def generate_system_content(search_string: str):
    return f"""
    You will receive JSON entries that are Google search results given for the query
    {search_string}. Of these, identify which is most useful to the original query, and justify why. 
    If non appear useful, say so and also justify why. 
    Relevancy is based on the following criteria: 
    the result must directly mention specific cases or policies relevant to the search term; 
    come from a credible and authoritative source; 
    provide detailed, actionable, and recent information specific to the mentioned location; 
    and directly address the terms 'misconduct' or 'liability insurance' as applicable. 
    Assess the depth of content and context to ensure it sufficiently addresses the query's needs.
    Give your answer in the following JSON format:
    {{
    "id": [whichever ID is most useful, or -1 if none],
      "rationale": [A rationale no more than three sentences in length.]
    }}
    """


def get_gpt_most_relevant_result(client: OpenAI, query_text: str, entries_json_str: str) -> MostRelevantResult:
    system_content = generate_system_content(query_text)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": entries_json_str}
        ]
    )
    d = json.loads(response.choices[0].message.content)
    return MostRelevantResult(
        result_id=d['id'],
        rationale=d['rationale']
    )


def get_search_results_as_json_string(search_results: list[SearchResult]) -> str:
    return json.dumps([asdict(search_result) for search_result in search_results])


if __name__ == "__main__":
    if not table_exists('relevant_search_gpt'):
        create_relevant_search_gpt_table()
    for _ in range(47):
        next_query_and_results = get_next_query_and_results()
        search_results_json_string = get_search_results_as_json_string(next_query_and_results.search_results)
        load_dotenv()
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        most_relevant_result = get_gpt_most_relevant_result(
            client=client,
            query_text=next_query_and_results.query_text,
            entries_json_str=search_results_json_string
        )
        upload_most_relevant_result(
            most_relevant_result=most_relevant_result,
            query_id=next_query_and_results.query_id
        )



