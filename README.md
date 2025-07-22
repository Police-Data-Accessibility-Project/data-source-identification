This is a multi-language repo containing scripts or tools for identifying and cataloguing Data Sources based on their URL and HTML content.

# Index

name | description of purpose
--- | ---
.github/workflows | Scheduling and automation
agency_identifier | Matches URLs with an agency from the PDAP database
annotation_pipeline | Automated pipeline for generating training data in our ML data source identification models. Manages common crawl, HTML tag collection, and Label Studio import/export
html_tag_collector | Collects HTML header, meta, and title tags and appends them to a JSON file. The idea is to make a richer dataset for algorithm training and data labeling.
identification_pipeline.py | The core python script uniting this modular pipeline. More details below.
llm_api_logic | Scripts for accessing the openai API on PDAP's shared account
source_collectors| Tools for extracting metadata from different sources, including CKAN data portals and Common Crawler
collector_db | Database for storing data from source collectors
collector_manager | A module which provides a unified interface for interacting with source collectors and relevant data
core | A module which integrates other components, such as collector_manager and collector_db
api | API for interacting with collector_manager, core, and collector_db
local_database | Resources for setting up a test database for local development
security_manager| A module which provides a unified interface for interacting with authentication and authorization |
tests | Unit and integration tests |
util | various utility functions |

## Installation

```
uv sync
```

## How to use

1. Create an .env file in this directory following the instructions in `ENV.md`
   1. If necessary, start up the database using `docker compose up -d` while in the `local_database` directory
2. Run `fastapi dev main.py` to start up the fast API server
3. In a browser, navigate to `http://localhost:8000/docs` to see the full list of API endpoints

Note that to access API endpoints, you will need to have a valid Bearer Token from the Data Sources API at `https://data-sources.pdap.io/api`

# Contributing

Thank you for your interest in contributing to this project! Please follow these guidelines:

- [These Design Principles](https://github.com/Police-Data-Accessibility-Project/meta/blob/main/DESIGN-PRINCIPLES.md) may be used to make decisions or guide your work.
- If you want to work on something, create an issue first so the broader community can discuss it.
- If you make a utility, script, app, or other useful bit of code: put it in a top-level directory with an appropriate name and dedicated README and add it to the index.

# Testing

Note that prior to running tests, you need to install [Docker](https://docs.docker.com/get-started/get-docker/) and have the Docker engine running.

Tests can be run by spinning up the `docker-compose-test.yml` file in the root directory. This will start a two-container setup, consisting of the FastAPI Web App and a clean Postgres Database. 

This can be done via the following command:

```bash
docker compose up -d
```

Following that, you will need to set up the uvicorn server using the following command:

```bash
docker exec data-source-identification-app-1 uvicorn api.main:app --host 0.0.0.0 --port 80
```

Note that while the container may mention the web app running on `0.0.0.0:8000`, the actual host may be `127.0.0.1:8000`.

To access the API documentation, visit `http://{host}:8000/docs`.

To run tests on the container, run:

```bash
docker exec data-source-identification-app-1 pytest /app/tests/automated
```

Be sure to inspect the `docker-compose.yml` file in the root directory -- some environment variables are dependant upon the Operating System you are using.

# Diagrams

## Identification pipeline plan

```mermaid
flowchart TD
    SourceCollectors["**Source Collectors:** scripts for creating batches of potentially useful URLs using different strategies"]
    Identifier["Batches are prepared for labeling by automatically collecting metadata and identifying low-hanging fruit properties"]
    SourceCollectorLabeling["Human labeling of missing or uncertain metadata takes place in Source Collector Retool app"]
    SourceCollectorReview["Human Final Review of the labeled sources, for submission or discard, in Retool"]
    API["Submitting sources to the Data Sources API when they are Relevant and have an **Agency, Record Type, and Name**"]

    SourceCollectors --> Identifier
    Identifier --> SourceCollectorLabeling
    SourceCollectorLabeling --> SourceCollectorReview
    SourceCollectorReview --> API
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
participant SC as Source Collector app
participant PDAP as PDAP API

loop create batches of URLs <br/>for human labeling
  SC ->> SC: Crawl for a new batch<br/> of URLs with common_crawler<br/> or other methods
  SC ->> SC: Add metadata to each batch<br/> with source_tag_collector
  SC ->> SC: Add labeling tasks in <br/> the Source Collector app

loop annotate URLs
  SC ->> SC: Users label using<br/>Retool interface
  SC ->> SC: Reviewers finalize <br/> and submit labels
end

loop update training data <br/> with new annotations
  SC ->> SC: Check for completed <br/> annotation tasks
  SC -->> PDAP: Submit labeled URLs to the app
  SC ->> HF: Write all annotations to <br/> training-urls dataset
  SC ->> SC: maintain batch status
end

loop model training
  HF ->> HF: retrain ML models with <br/>updated data using <br/>trainer in hugging_face
end

end
```

# Docstring and Type Checking

Docstrings and Type Checking are checked using the [pydocstyle](https://www.pydocstyle.org/en/stable/) and [mypy](https://mypy-lang.org/)
modules, respectively. When making a pull request, a Github Action (`python_checks.yml`) will run and, 
if it detects any missing docstrings or type hints in files that you have modified, post them in the Pull Request.

These will *not* block any Pull request, but exist primarily as advisory comments to encourage good coding standards.

Note that `python_checks.yml` will only function on pull requests made from within the repo, not from a forked repo.
