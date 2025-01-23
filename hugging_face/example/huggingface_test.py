import evaluate
import numpy as np
from datasets import ClassLabel
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from transformers import TrainingArguments, Trainer
from transformers import pipeline

MODEL = "distilbert-base-uncased"
MAX_STEPS = 500

dataset = load_dataset("PDAP/urls")
tokenizer = AutoTokenizer.from_pretrained(MODEL)
labels = ClassLabel(names_file="labels.txt")

def tokenize_function(batch):
    tokens = tokenizer(batch["url"], padding="max_length", truncation=False)
    tokens["label"] = labels.str2int(batch["label"])
    return tokens

tokenized_datasets = dataset.map(tokenize_function, batched=True)
# Add custom labels to the results
tokenized_datasets = tokenized_datasets.cast_column("label", labels)

# Shuffles the dataset, a smaller range can be selected to speed up training
# Selecting a smaller range may come at the cost of accuracy and may cause errors if some labels end up being excluded from the dataset
train_dataset = tokenized_datasets["train"].shuffle(seed=42)#.select(range(1000))
eval_dataset = tokenized_datasets["test"].shuffle(seed=42)#.select(range(1000))

classifier = pipeline("text-classification", model=MODEL, framework="pt", tokenizer=tokenizer)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=28)
training_args = TrainingArguments(output_dir="test_trainer_1.1", evaluation_strategy="epoch", max_steps=MAX_STEPS)#, push_to_hub=True)
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
    compute_metrics=compute_metrics
)

trainer.train()

# These will push a new model version to the Hugging Face Hub upon training completion
#trainer.push_to_hub("PDAP/url-classifier-test")
#tokenizer.push_to_hub("PDAP/url-classifier-test")
