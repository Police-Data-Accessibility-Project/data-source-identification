import pandas as pd
from datasets import load_dataset, concatenate_datasets

from hugging_face.url_relevance.dataclasses.TrainTestDataframes import TrainTestDataframes

MODEL = "distilbert-base-uncased"
DATASET = "PDAP/urls-relevance"
MAX_STEPS = 1000
LABELS = ["Relevant", "Irrelevant"]
LABEL_COL = "label"


def str2int(label: str) -> int:
    return LABELS.index(label)


def set_up_dataset() -> TrainTestDataframes:
    dataset = load_dataset(DATASET)
    dataset_concat = concatenate_datasets([dataset["train"], dataset["test"]])
    dataset_shuffle = dataset_concat.shuffle()
    dataset_split = dataset_shuffle.train_test_split(test_size=0.15)
    return TrainTestDataframes(
        train=pd.DataFrame(dataset_split["train"]),
        test=pd.DataFrame(dataset_split["test"])
    )

def apply_labels(ttd: TrainTestDataframes):
    num_labels = len(LABELS)
    for df in ttd.get_as_list():
        df[LABEL_COL] = df[LABEL_COL].apply(str2int)