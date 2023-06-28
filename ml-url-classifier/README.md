# ML URL Classifier

## Getting Started
1. Clone this repository
    ```bash
    git clone https://github.com/Police-Data-Accessibility-Project/data-source-identification.git pdap-data-source-identification
    cd pdap-data-source-identification/ml-url-classifier
    ```
2. Add a CSV file named "input.csv" to the `data/` directory. It should contain one column of urls called "url"
3. In Mac/Linux, create a new virtual environment and activate it.

```
$python3 -m venv venv
$source venv/bin/activate
(venv) $
```

4. Now install the required python libraries:

```commandline
$pip install -r requirements.txt
```
5. Run the classifier.py script. It will generate a results.csv file in the `data/` directory (you can ignore the warning it generates).

```commandline
$python3 classifier.py
```