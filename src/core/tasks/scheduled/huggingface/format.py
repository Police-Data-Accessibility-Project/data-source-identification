from datasets import Dataset
import polars as pl

def format_as_huggingface_dataset(df: pl.DataFrame) -> Dataset:
    return Dataset.from_polars(df)