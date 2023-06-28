import sys
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression

RANDOM_SEED = 1

def core():
    # Fit the model to the training data
    training_df = pd.read_csv("data/training_data.csv")
    x_train, x_test, y_train, y_test = train_test_split(
        training_df["url"], training_df["label"], random_state=RANDOM_SEED
    )
    pipeline_ls = make_pipeline(
        CountVectorizer(
            tokenizer=RegexpTokenizer(r"[A-Za-z]+").tokenize, stop_words="english"
        ),
        LogisticRegression(max_iter=training_df.shape[0]),
    )
    pipeline_ls.fit(x_train, y_train)

    # Ingest data to be classified
    test_df = pd.read_csv("data/input.csv")
    # Remove extra characters from 'url' column
    test_df["url"] = (
        test_df.url.str.replace("https://", "", regex=False)
        .str.replace("http://", "", regex=False)
        .str.replace("www.", "", regex=False)
    )
    # Remove null rows
    test_df.dropna(subset=["url"], inplace=True)
    print(test_df.info())
    # Remove duplicate rows of urls
    test_df["url"].drop_duplicates(inplace=True)
    # Use the model to predict the relevance of ingested urls
    test_df["predictions"] = pipeline_ls.predict(test_df["url"])
    test_df[["url", "predictions"]].to_csv("data/results.csv", index=False)

    return "URL classification complete!"

if __name__ =="__main__":
    print(core())