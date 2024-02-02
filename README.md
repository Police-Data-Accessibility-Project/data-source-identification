This is a multi-language repo containing scripts or tools for identifying Data Sources by their URL and HTML content.

# Index

name | description of purpose
--- | ---
Identification Pipeline | The core python script of a modular pipeline. More details below.
hf-testing | Utilities for interacting with our machine learning space at [Hugging Face](https://huggingface.co/PDAP)
HTML tag collector | Collects HTML header, meta, and title tags and appends them to a JSON file. The idea is to make a richer dataset for algorithm training and data labeling.
ML URL Classifier (work in progress) | Classifies a set of URLs given by a CSV file using the KNN and Logistic Regression algorithms. This is a work in progress with one function experiment on a small labeled dataset (~400 observations, 1 feature, 2 classes). Pending progress involves testing the existing workflow in `main.ipynb` against a larger labeled dataset and including more labels in the classification problem.
openai-playground | Scripts for accessing the openai API on PDAP's shared account

# Identification pipeline
In an effort to build out a fully automated system for identifying and cataloguing new data sources, this pipeline:
- Checks potential new data sources against all those already in the database
- Runs non-duplicate sources through the `HTML tag collector` for use in ML training
- Checks the hostnames against those of the agencies in the database

## How to use

1. Create an .env file in this directory with these contents, or set the environment variable another way: `VUE_APP_PDAP_API_KEY=KeyGoesHere`
2. Create a file in this directory containing a list of urls to be identified, or modify the existing `urls.csv` file. This requires one URL per line with at least a `url` column.
3. Run `python3 identification_pipeline.py urls.csv`
4. Results will be written in the same directory as results.csv
5. If importing "identification_pipeline_main" function, it expects a dataframe as an argument and returns a resulting dataframe

# Contributing

Thank you for your interest in contributing to this project! Please follow these guidelines:

- If you want to work on something, create an issue first so the broader community can discuss it.
- If you make a utility, script, app, or other useful bit of code: put it in a top-level directory with an appropriate name and dedicated README and add it to the index.

# Pipeline flow & operations

Each of these steps may be attempted with regex, human identification, or machine learning. Once a property is in the JSON metadata, 

```mermaid
%% Here's a guide to mermaid syntax: https://mermaid.js.org/syntax/flowchart.html

flowchart TD
A["Start with a list of URLs
in JSON format"]
B["Check for duplicates in the pipeline's
training data"]
C["Make an HTTP request to the URL
and append some JSON metadata"]
D["Determine whether the URL is about one of our
`agency_types` (police, courts, jails)"]
E["Determine which `agency` is described"]
F["Determine if this is an `individual record`.
We're after parent data sources."]
G["Add `name`, `description`, `record_type`
based on request content"]
H["Identify other metadata
based on our pipeline"]
I["Submit Data Sources with `agency`, `name`,
`description`, and `record_type` to the
approval queue"]
J["Use newly approved Data Sources to
train machine learning algorithms"]
reject["Reject the URL"]
manual["Human-identify and
resubmit"]

subgraph Happy path
A --> B
B --> C
C --> D
D -- yes --> E
E -- found --> F
F --> G
G --> H
H -- minimum criteria met --> I
I --> J
end

D -- no --> reject
E -- not found --> manual
H -- incomplete --> manual
```
