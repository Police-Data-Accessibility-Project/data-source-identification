This is a multi-language repo containing scripts or tools for identifying Data Sources by their URL and HTML content.

# Index

name | description of purpose
--- | ---
Identification Pipeline | The core python script of a modular pipeline. More details below.
agency_identifier | Matches URLs with an agency from the PDAP database
common_crawler | interfaces with the Common Crawl dataset to extract urls, creating batches to identify or annotate
hugging_face | Utilities for interacting with our machine learning space at [Hugging Face](https://huggingface.co/PDAP)
html_tag_collector | Collects HTML header, meta, and title tags and appends them to a JSON file. The idea is to make a richer dataset for algorithm training and data labeling.
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


## Training models by batching and annotating URLs

```mermaid
%% Here's a guide to mermaid syntax: https://mermaid.js.org/syntax/flowchart.html

sequenceDiagram

participant HF as Hugging Face
participant GH as GitHub
participant LS as Label Studio
participant PDAP as PDAP API

loop create batches of URLs <br/>for human labeling
  GH ->> GH: Crawl for a new batch<br/> of URLs with common_crawler<br/> or other methods
  GH ->> GH: Add metadata to each batch<br/> with source_tag_collector
  GH ->> HF: Add the batch <br/> of URLs to a dataset
  HF -->> GH: Confirm batch created
  GH ->> LS: Create labeling tasks <br/> from the batch
  LS -->> GH: Confirm tasks created
  GH ->> GH: add batches to a log file <br/> in this repo with URL<br/> and batch IDs
end

loop annotate URLs
  LS ->> LS: Users annotate using<br/>Label Studio interface
end

loop update training data <br/> with new annotations
  GH ->> LS: Check for completed <br/> annotation tasks
  LS -->> GH: Confirm new annotations <br/> since last check
  GH ->> HF: Write new annotations to <br/> training dataset
  GH ->> GH: log batch status to file
end

loop check PDAP database <br/>for new sources
  GH ->> PDAP: Trigger action to check <br/> for new data sources
  PDAP -->> GH: confirm sources available <br/> since last check
  GH ->> GH: Collect additional metadata
  GH ->> HF: Write sources to <br/> training dataset
end

loop model training
  GH ->> HF: retrain ML models with <br/>updated data using <br/>trainer in hugging_face
end

```

## Using trained models to identify URLs

Each of these steps may be attempted with regex, human identification, or machine learning. We combine several machine learning (ML) models, each focusing on a specific task or property.

```mermaid
%% Here's a guide to mermaid syntax: https://mermaid.js.org/syntax/flowchart.html

sequenceDiagram

participant HF as Hugging Face
participant GH as GitHub
participant PDAP as PDAP API

GH ->> GH: Start with a batch of URLs from <br/> common_crawler or another source <br/> with a batch log file
GH ->> PDAP: Check for duplicate URLs
PDAP ->> GH: Report back duplicates to remove
GH ->> HF: Create batch for identification
HF -->> GH: Confirm batch created

loop trigger Hugging Face models to add <br/>labels to the same dataset
  GH ->> HF: Check URLs for relevance <br/> to police, courts, or jails
  HF -->> GH: complete
  GH ->> HF: Check relevant URLs for <br/> "individual records"
  HF -->> GH: complete
  note over HF,GH: Ignore irrelevant and <br/> individual record sources <br/> for following steps
  GH ->> HF: Identify an agency or <br/> geographic area
  GH ->> HF: Identify record_type, <br/> name, and description
  HF -->> GH: Confirm batch complete
end

GH ->> PDAP: Submit URLs for manual approval
```
