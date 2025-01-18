import pandas as pd
from datasets import load_dataset, Dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from hugging_face.url_relevance.constants import TRAINING_URLS_DATASET


def main():
    dataset: Dataset = load_dataset(TRAINING_URLS_DATASET)['train']

    df: pd.DataFrame = dataset.to_pandas()

    # Remove all URLS that are None
    dataset_dict = df.dropna(subset=['url']).to_dict()

    urls = list(dataset_dict["url"].values())
    relevant_labels = list(dataset_dict["relevant"].values())

    X_train, X_test, y_train, y_test = train_test_split(urls, relevant_labels, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(
        analyzer='char',  # Analyze at the character level for URLs
        ngram_range=(3, 6),  # Use character-level n-grams (e.g., trigrams, hexagrams)
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Train Logistic Regression
    model = LogisticRegression()
    model.fit(X_train_tfidf, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test_tfidf)
    print(classification_report(y_test, y_pred))


if __name__ == "__main__":
    main()