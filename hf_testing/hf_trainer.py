from datasets import load_dataset
from datasets import ClassLabel
from transformers import pipeline
from transformers import AutoModelForSequenceClassification
from transformers import TrainingArguments, Trainer, get_linear_schedule_with_warmup, AdamW
from transformers import AutoTokenizer
import numpy as np
import evaluate

MODEL = "distilbert-base-uncased"

dataset = load_dataset("PDAP/urls-and-headers")
tokenizer = AutoTokenizer.from_pretrained(MODEL)
labels = ClassLabel(names_file="data/high-freq-labels.txt")
features = ['url', 'http_response', 'html_title', 'meta_description', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

labels_to_keep = set(labels.names)

# Filter the dataset based on labels
filtered_dataset = dataset.filter(lambda example: example['label'] in labels_to_keep)

def tokenize_function(batch):
    # Combine relevant features into a single string for tokenization
    text_to_tokenize = " ".join([str(batch[feature]) for feature in features])
    tokens = tokenizer(text_to_tokenize, padding='max_length', truncation=True)
    tokens["label"] = labels.str2int(batch["label"])
    return tokens

# Tokenize the datasets
tokenized_train_dataset = filtered_dataset["train"].map(tokenize_function, batched=False)
tokenized_test_dataset = filtered_dataset["test"].map(tokenize_function, batched=False)

# Optionally, you can cast the "label" column to ClassLabel
tokenized_train_dataset = tokenized_train_dataset.cast_column("label", labels)
tokenized_test_dataset = tokenized_test_dataset.cast_column("label", labels)

classifier = pipeline("text-classification", model=MODEL, framework="pt", tokenizer=tokenizer)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=18)

training_args = TrainingArguments(
    output_dir="distilbert_1.1", 
    evaluation_strategy="epoch", 
    save_strategy='epoch', 
    num_train_epochs=2,
    learning_rate=2e-5,  # Initial learning rate
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=100,  # Number of warmup steps
    weight_decay=0.01 # Weight decay coefficient)
)
optimizer = AdamW(model.parameters(), lr=training_args.learning_rate)  # Define the optimizer
metric = evaluate.load("accuracy")

# Calculate the total number of training steps
total_steps = len(tokenized_train_dataset) // training_args.per_device_train_batch_size * training_args.num_train_epochs

# Create the learning rate scheduler
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=training_args.warmup_steps,
    num_training_steps=total_steps
)

eval_predictions = []
eval_labels = []

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)

    #store the predictions and labels
    eval_predictions.extend(predictions.tolist())
    eval_labels.extend(labels.tolist())
    
    return metric.compute(predictions=predictions, references=labels)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_test_dataset,
    compute_metrics=compute_metrics,
    optimizers = (optimizer, scheduler)
)

trainer.train()