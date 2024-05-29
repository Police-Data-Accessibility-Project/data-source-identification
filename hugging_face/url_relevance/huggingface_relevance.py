from datasets import load_dataset
from datasets import concatenate_datasets
from transformers import TrainingArguments, Trainer
from transformers import AutoTokenizer
from multimodal_transformers.model import AutoModelWithTabular, TabularConfig
from transformers import AutoConfig
from multimodal_transformers.data import load_data
import numpy as np
import pandas as pd
import evaluate


""" This model is trained using website data from a list of potentially relevant URLs.
    A "relevant" URL is one that related to criminal justice. A "relevant" website does not necessarily mean it is a "good" data source.
    The latest version of the model can be found here: https://huggingface.co/PDAP/url-relevance
"""

MODEL = "distilbert-base-uncased"
DATASET = "PDAP/urls-relevance"
MAX_STEPS = 1000


def str2int(label):
    return labels.index(label)


dataset = load_dataset(DATASET)
dataset = concatenate_datasets([dataset["train"], dataset["test"]])
dataset = dataset.shuffle()
dataset = dataset.train_test_split(test_size=0.15)
train_df = pd.DataFrame(dataset["train"])
test_df = pd.DataFrame(dataset["test"])

labels = ["Relevant", "Irrelevant"]
num_labels = len(labels)
label_col = "label"
train_df["label"] = train_df["label"].apply(str2int)
test_df["label"] = test_df["label"].apply(str2int)

text_cols = [
    "url_path",
    "html_title",
    "keywords",
    "meta_description",
    "root_page_title",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]  # "url", "http_response"
empty_text_values = ['[""]', None, "[]", '""']
tokenizer = AutoTokenizer.from_pretrained(MODEL)

train_dataset = load_data(
    train_df,
    text_cols,
    tokenizer,
    label_col,
    label_list=labels,
    sep_text_token_str=tokenizer.sep_token,
    empty_text_values=empty_text_values,
)
test_dataset = load_data(
    test_df,
    text_cols,
    tokenizer,
    label_col,
    label_list=labels,
    sep_text_token_str=tokenizer.sep_token,
    empty_text_values=empty_text_values,
)

config = AutoConfig.from_pretrained(MODEL)
tabular_config = TabularConfig(
    num_labels=num_labels,
    combine_feat_method="text_only",
)
config.tabular_config = tabular_config
config.max_position_embeddings = 2048

model = AutoModelWithTabular.from_pretrained(MODEL, config=config, ignore_mismatched_sizes=True)

metric = evaluate.load("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    # logits_shape = logits[0].shape if isinstance(logits, tuple) else logits.shape
    predictions = np.argmax(logits[0], axis=-1) if isinstance(logits, tuple) else np.argmax(logits, axis=-1)
    labels = labels.flatten()
    predictions = predictions.flatten()

    return metric.compute(predictions=predictions, references=labels)


training_args = TrainingArguments(
    output_dir="./url_relevance",
    logging_dir="./url_relevance/runs",
    overwrite_output_dir=True,
    do_train=True,
    max_steps=MAX_STEPS,
    evaluation_strategy="steps",
    eval_steps=25,
    logging_steps=25,
    weight_decay=0.1,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
