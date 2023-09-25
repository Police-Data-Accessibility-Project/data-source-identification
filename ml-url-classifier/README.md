# ML URL Classifier

## Getting Started
1. Clone this repository
    ```bash
    git clone https://github.com/Police-Data-Accessibility-Project/data-source-identification.git pdap-data-source-identification
    cd pdap-data-source-identification/ml-url-classifier
    ```
2. Add a CSV file named "training_data.csv" to the `data/` directory. It should contain one column of urls called "url" and one called "label" to indicate if the url is "relevant" or "irrelevant". This is used for training the algorithm in how to assign each label to unseen urls
3. Add a CSV file named "input.csv" to the `data/` directory. It should contain at least one column of urls called "url". This is used for assigning labels to unlabelled data
4. In Mac/Linux, create a new virtual environment and activate it.

```
$python3 -m venv venv
$source venv/bin/activate
(venv) $
```

5. Now install the required python libraries:

```commandline
$pip install -r requirements.txt
```
6. Run the classifier.py script. It will generate a results.csv file in the `data/` directory (you can ignore the warning it generates).

```commandline
$python3 classifier.py
```
