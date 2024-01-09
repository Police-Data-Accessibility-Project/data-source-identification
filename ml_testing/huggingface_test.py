from datasets import load_dataset
from datasets import ClassLabel
from transformers import pipeline
from transformers import AutoModelForSequenceClassification
from transformers import TrainingArguments, Trainer
from transformers import AutoTokenizer
import numpy as np
import evaluate

dataset = load_dataset("PDAP/urls")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
labels = ClassLabel(names_file="labels.txt")

def tokenize_function(batch):
    tokens = tokenizer(batch["url"], padding="max_length", truncation=False)
    tokens["label"] = labels.str2int(batch["label"])
    return tokens

tokenized_datasets = dataset.map(tokenize_function, batched=True)
train_dataset = tokenized_datasets["train"].shuffle(seed=42)#.select(range(1000))
eval_dataset = tokenized_datasets["test"].shuffle(seed=42)#.select(range(1000))

classifier = pipeline("sentiment-analysis")
model = AutoModelForSequenceClassification.from_pretrained("bert-base-cased", num_labels=28)
training_args = TrainingArguments(output_dir="test_trainer", evaluation_strategy="epoch")
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
