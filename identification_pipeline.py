import requests
import os
import polars as pl
from html_tag_collector.collector import collector_main

identify_df = pl.read_csv("urls_to_identify.csv")
identify_df.unique()
identify_df.fill_null(""''"")
identify_df = identify_df.filter(pl.col("url").is_not_null())

api_key = "Bearer " + os.getenv("PDAP_API_KEY")
response = requests.get("https://data-sources.pdap.io/archives", headers={"Authorization": api_key})
data = response.json()
data_sources_df = pl.DataFrame(data)

duplicate_check_df = identify_df.join(data_sources_df, left_on="url", right_on="source_url", how="outer")
non_duplicates_df = duplicate_check_df.filter(pl.col("id").is_null()).select(pl.col("url","id"))

tagged_df = collector_main(non_duplicates_df)

print(tagged_df)
