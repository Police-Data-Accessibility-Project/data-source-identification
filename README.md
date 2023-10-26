This is a multi-language repo containing scripts or tools for identifying Data Sources by their URL and HTML content.

This is the issue which spawned the repo: https://github.com/Police-Data-Accessibility-Project/planning/issues/196

# Index

name | description of purpose
--- | ---
Identification Pipeline | More details below
HTML tag collector | Collects HTML header, meta, and title tags and appends them to a JSON file. The idea is to make a richer dataset for algorithm training and data labeling.
ML URL Classifier (work in progress) | Classifies a set of URLs given by a CSV file using the KNN and Logistic Regression algorithms. This is a work in progress with one function experiment on a small labeled dataset (~400 observations, 1 feature, 2 classes). Pending progress involves testing the existing workflow in `main.ipynb` against a larger labeled dataset and including more labels in the classification problem.

## Identification pipeline
In an effort to build out a fully automated system for identifying and cataloguing new data sources, this pipeline:
1. Checks potential new data sources against all those already in the database
2. Runs non-duplicate sources through the `HTML tag collector` for use in ML training
3. Checks the hostnames against those of the agencies in the database


# Contributing

If you make a useful bit of code, put it in a top-level directory with an appropriate name and dedicated README. Also, add it to the index.
