import pandas as pd
from datasets import load_dataset, concatenate_datasets

from hugging_face.url_relevance.constants import URL_RELEVANCE_DATASET
from hugging_face.url_relevance.dataclasses.TrainTestDataframes import TrainTestDataframes


def set_up_dataset(
        dataset_name: str = URL_RELEVANCE_DATASET,
        test_split_size: float = 0.15
) -> TrainTestDataframes:
    dataset = load_dataset(dataset_name)
    dataset_concat = concatenate_datasets([dataset["train"], dataset["test"]])
    dataset_shuffle = dataset_concat.shuffle()
    dataset_split = dataset_shuffle.train_test_split(test_size=test_split_size)
    return TrainTestDataframes(
        train=pd.DataFrame(dataset_split["train"]),
        test=pd.DataFrame(dataset_split["test"])
    )

def apply_label(ttd: TrainTestDataframes, label_col: str, labels: list[str]):
    def str2int(label: str) -> int:
        return labels.index(label)

    for df in ttd.get_as_list():
        df[label_col] = df[label_col].apply(str2int)