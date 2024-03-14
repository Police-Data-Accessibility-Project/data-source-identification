import polars as pl
import pytest

from html_tag_collector.collector import process_in_batches

sample_json_data = [{
    "id": 1,
    "url": "https://pdap.io",
    "label": "Label"
}, {
    "id": 2,
    "url": "https://pdapio.io",
    "label": "Label"
}, {
    "id": 3,
    "url": "https://pdap.dev",
    "label": "Label"
}, {
    "id": 4,
    "url": "https://pdap.io/404test",
    "label": "Label"
}, {
    "id": 5,
    "url": "https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html",
    "label": "Label"
}
]


def test_collector_main():
    """
    Test main function from collector module for manual inspection
    Involves live connection to and pulling of internet data
    """
    df = pl.DataFrame(sample_json_data)

    cumulative_df = process_in_batches(
        df=df,
        render_javascript=False
    )

    print(cumulative_df)
    # print data from each row, for each column
    for i in range(len(cumulative_df)):
        for col in cumulative_df.columns:
            print(f"{col}: {cumulative_df[col][i]}")
