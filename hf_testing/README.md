# URL Classifier Test

This is a test model for URL classification related to criminal justice.

You can view the model repository on Hugging Face here: [https://huggingface.co/PDAP/url-classifier-test](https://huggingface.co/PDAP/url-classifier-test)

## Models

The models used for training are:

- BERT (bert-base-uncased) - [https://huggingface.co/docs/transformers/model_doc/bert](https://huggingface.co/docs/transformers/model_doc/bert)
- DistilBERT (distilbert-base-uncased) - [https://huggingface.co/docs/transformers/model_doc/distilbert](https://huggingface.co/docs/transformers/model_doc/distilbert)

Training a model with BERT took about 17 hours for 2 epochs (training time is affected by hardware used and can be more or less depending on it). DistilBERT is a lightweight version of BERT and took about 6 hours of training for 1.4 epochs while only losing a few percentage points of accuracy. For testing purposes we can use DistilBERT for speedier training and BERT to further refine the model if necessary.

## Accuracy

The model accuracy is currently about 60% when predicting from a pool of 28 labels.

You can view accuracy and various other training metrics on the model page here: [https://huggingface.co/PDAP/url-classifier-test/tensorboard](https://huggingface.co/PDAP/url-classifier-test/tensorboard)

Things that can increase accuracy include:

- Training with BERT
- Increasing the `max_steps` parameter of the `TrainingArguments()` function
- Expanding the database, especially having more training examples available for the less used labels
- Adding HTML headers for websites into the mix to give the model more information to work with
- MAYBE: use the 'precision' evaluation strategy instead of 'accuracy' - more testing will be required if this would improve overall accuracy

Most of these methods will come at the cost of training time.

`MAX_STEPS` is set to 500 by default, or about 1.4 epochs of training; at this point in the training the accuracy would increase by about 1% per 200 steps, meaning much more training time would be needed to increase the accuracy significantly and may have a point where it plateaus and cannot get any more accurate.

## Dataset

The dataset used for training can be found here [https://huggingface.co/datasets/PDAP/urls](https://huggingface.co/datasets/PDAP/urls)

One dataset is for training data and the other is for accuracy testing

## Files

- `huggingface_test.py` - Script that starts the model training process
- `labels.txt` - Text file containing all possible labels that are used for prediction. If a label does not appear in the dataset, it may cause and error. If a label appears in the dataset and is not in the labels file, it will cause an error
- `clean_data.py` - Takes a CSV file and splits it into two, one for training and the other for evaluation
- `train-urls.csv` - CSV of URLs used for model training
- `test-urls.csv` - CSV of URLs used for model accuracy evaluation

## How to Run

### Training script

You can run the training script by installing the libraries in `requirements.txt` and running `python3 huggingface_test.py`. Everythning should be setup and ready to go. You can change the training model by editing the `MODEL` variable and number of training steps with the `MAX_STEPS` variable.

### Using the trained model

You can test the trained model by entering one link at a time in the Inference API GUI box on the model's [homepage](https://huggingface.co/PDAP/url-classifier-test).

You can also consume the trained model programmatically using Hugging Face's Inference API. Learn more about that here: [https://huggingface.co/docs/api-inference/quicktour](https://huggingface.co/docs/api-inference/quicktour)
