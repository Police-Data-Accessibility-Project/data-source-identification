This is a multi-language repo containing scripts or tools for identifying and cataloguing Data Sources based on their URL and HTML content.

# Index

name | description of purpose
--- | ---
.github/workflows | Scheduling and automation
agency_identifier | Matches URLs with an agency from the PDAP database
annotation_pipeline | Automated pipeline for generating training data in our ML data source identification models. Manages common crawl, HTML tag collection, and Label Studio import/export
html_tag_collector | Collects HTML header, meta, and title tags and appends them to a JSON file. The idea is to make a richer dataset for algorithm training and data labeling.
hugging_face | Utilities for interacting with our machine learning space at [Hugging Face](https://huggingface.co/PDAP)
identification_pipeline.py | The core python script uniting this modular pipeline. More details below.
openai-playground | Scripts for accessing the openai API on PDAP's shared account
source_collectors| Tools for extracting metadata from different sources, including CKAN data portals and Common Crawler
collector_db | Database for storing data from source collectors
collector_manager | A module which provides a unified interface for interacting with source collectors and relevant data
core | A module which integrates other components, such as collector_manager and collector_db
api | API for interacting with collector_manager, core, and collector_db
local_database | Resources for setting up a test database for local development

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

# Testing

Tests can be run by spinning up the `docker-compose-test.yml` file in the root directory. This will start a two-container setup, consisting of the FastAPI Web App and a clean Postgres Database. To run tests on the container, run:

```bash
docker compose up -d
docker exec data-source-identification-app-1 pytest /app/tests/test_automated
```

Be sure to inspect the `docker-compose.yml` file in the root directory -- some environment variables are dependant upon the Operating System you are using.

# Diagrams

## Identification pipeline plan

```mermaid
flowchart TD
    SourceCollectors["**Source Collectors:** automatic searches, citation follower, portal scrapers, agency crawlers, common crawler"]
    Logging["Logging source collection attempts"]
    API["Submitting sources to the **Data Sources API** for approval"]
    Identifier["**Data Source Identifier:** agency matcher, duplicate checker, tag collector, ML metadata labelers"]
    LabelStudio["Human labeling of missing or uncertain metadata in LabelStudio"]

    Identifier --> LabelStudio
    Identifier ---> API
    LabelStudio --> API
    Identifier --> Logging

    SourceCollectors --> Identifier

    API --> Search["Allowing users to search for data and browse maps"]
    Search --> Sentiment["Capturing user sentiment and overall database utility"]
    API --> MLModels["Improving ML metadata labelers: relevance, agency, record type, etc"]
    API --> Missingness["Documenting data we have searched for and found to be missing"]
    Missingness --> Maps["Mapping our progress and the overall state of data access"]

    %% Default class for black stroke
    classDef default fill:#fffbfa,stroke:#000,stroke-width:1px,color:#000;

    %% Custom styles
    class API gold;
    class Search lightgold;
    class MLModels,Missingness lightergold;
    class SourceCollectors,Identifier byzantium

    %% Define specific classes
    classDef gray fill:#bfc0c0
    classDef gold fill:#d5a23c
    classDef lightgold fill:#fbd597
    classDef lightergold fill:#fdf0dd
    classDef byzantium fill:#dfd6de
```

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
  GH ->> LS: Add the batch as <br/> labeling tasks in <br/> the Label Studio project
  LS -->> GH: Confirm batch created
  GH ->> GH: add batches to a log file <br/> in this repo with URL<br/> and batch IDs
end

loop annotate URLs
  LS ->> LS: Users annotate using<br/>Label Studio interface
end

loop update training data <br/> with new annotations
  GH ->> LS: Check for completed <br/> annotation tasks
  LS -->> GH: Confirm new annotations <br/> since last check
  GH ->> HF: Write new annotations to <br/> training-urls dataset
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

# Docstring and Type Checking

Docstrings and Type Checking are checked using the [pydocstyle](https://www.pydocstyle.org/en/stable/) and [mypy](https://mypy-lang.org/)
modules, respectively. When making a pull request, a Github Action (`python_checks.yml`) will run and, 
if it detects any missing docstrings or type hints in files that you have modified, post them in the Pull Request.

These will *not* block any Pull request, but exist primarily as advisory comments to encourage good coding standards.

Note that `python_checks.yml` will only function on pull requests made from within the repo, not from a forked repo.
