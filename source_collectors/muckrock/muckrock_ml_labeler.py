"""
Utilizes a fine-tuned model to label a dataset of URLs.
"""

import argparse

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def load_dataset_from_command_line() -> pd.DataFrame:
    parser = argparse.ArgumentParser(description="Load CSV file into a pandas DataFrame.")
    parser.add_argument("--csv_file", type=str, required=True, help="Path to the CSV file")
    args = parser.parse_args()
    return pd.read_csv(args.csv_file)


def create_combined_text_column(df: pd.DataFrame) -> None:
    # Combine multiple columns (e.g., 'url', 'html_title', 'h1') into a single text field for each row
    columns_to_combine = [
        "url_path",
        "html_title",
        "h1",
    ]  # Add other columns here as needed
    df["combined_text"] = df[columns_to_combine].apply(
        lambda row: " ".join(row.values.astype(str)), axis=1
    )


def get_list_of_combined_texts(df: pd.DataFrame) -> list[str]:
    # Convert the combined text into a list
    return df["combined_text"].tolist()


def save_labeled_muckrock_dataset_to_csv():
    df.to_csv("labeled_muckrock_dataset.csv", index=False)


def create_predicted_labels_column(df: pd.DataFrame, predicted_labels: list[str]) -> None:
    df["predicted_label"] = predicted_labels


def map_predictions_to_labels(model, predictions) -> list[str]:
    labels = model.config.id2label
    return [labels[int(pred)] for pred in predictions]


def get_predicted_labels(texts: list[str]) -> list[str]:
    # Load the tokenizer and model
    model_name = "PDAP/fine-url-classifier"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()
    # Tokenize the inputs
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    # Perform inference
    with torch.no_grad():
        outputs = model(**inputs)
    # Get the predicted labels
    predictions = torch.argmax(outputs.logits, dim=-1)
    # Map predictions to labels
    predicted_labels = map_predictions_to_labels(model=model, predictions=predictions)

    return predicted_labels


if __name__ == "__main__":
    df = load_dataset_from_command_line()
    # TODO: Check for existence of required columns prior to further processing
    create_combined_text_column(df=df)

    texts = get_list_of_combined_texts(df=df)

    predicted_labels = get_predicted_labels(texts=texts)
    # Add the predicted labels to the dataframe and save
    create_predicted_labels_column(df=df, predicted_labels=predicted_labels)

    save_labeled_muckrock_dataset_to_csv()