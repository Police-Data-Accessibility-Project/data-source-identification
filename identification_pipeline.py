import requests
import os
import polars as pl
import sys
from html_tag_collector.collector import collector_main
from agency_identifier.identifier import match_urls_to_agencies_and_clean_data
from datetime import datetime as dt
from dotenv import load_dotenv

load_dotenv()

def identification_pipeline_main(df):
    df.unique()
    df.fill_null("")
    identify_df = df.filter(pl.col("url").is_not_null())

    api_key = "Bearer " + os.getenv("VUE_APP_PDAP_API_KEY")
    response = requests.get("https://data-sources.pdap.io/api/archives", headers={"Authorization": api_key})
    data = response.json()
    data_sources_df = pl.DataFrame(data)
    duplicate_check_df = identify_df.join(data_sources_df, left_on="url", right_on="source_url", how="outer")
    non_duplicates_df = duplicate_check_df.filter(pl.col("id").is_null()).select(pl.col("url","id"))
    tagged_df = collector_main(non_duplicates_df)
    identified_df = match_urls_to_agencies_and_clean_data(tagged_df)

    return identified_df


if __name__ == "__main__":
    df = pl.read_csv(sys.argv[1])
    identified_df = identification_pipeline_main(df)
    identified_df.write_csv("results.csv")