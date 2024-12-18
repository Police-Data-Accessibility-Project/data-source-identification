# Annotation Pipeline

This Python script automates the process of crawling for relevant URLs, scraping HTML content from those pages, formatting the data as Label Studio tasks, and uploading them to Label Studio for annotation.

## Features

- **Common Crawl Integration**: Initiates the Common Crawl script to crawl for relevant URLs based on specified parameters such as Common Crawl ID, URL type, keyword, and number of pages to process.

- **HTML Tag Collector**: Collects HTML tags from the crawled URLs using the tag collector script.

- **Label Studio Tasks**: Formats the collected data into tasks suitable for Label Studio annotation, including pre-annotation support for assumed record types.

- **Upload to Label Studio**: Uploads the tasks to Label Studio for review and annotation.

## Setup

1. Create venv and install Python dependencies (if not done previously)
   (assuming these are run within the annotation_pipeline/ folder):
   - `python -m venv annotation-pipeline-env`
   - `source annotation-pipeline-env`
   - `pip install -r requirements.txt`

2. Setup Environment variables in data_source_identification/.env
   - HUGGINGFACE_ACCESS_TOKEN=...
   - LABEL_STUDIO_ACCESS_TOKEN=...
   - LABEL_STUDIO_PROJECT_ID=...
   - LABEL_STUDIO_ORGANIZATION_ID=...

## Usage

Run from the parent directory (data-source-identification/)

The output logs from common crawl will be stored in `annotation_pipeline/data` by default. This can be modified by editing the `annotation_pipeline/config.ini` file.

`python annotation_pipeline/populate_labelstudio.py common_crawl_id url keyword --pages num_pages [--record-type record_type]`

- `common_crawl_id`: ID of the Common Crawl Corpus to search
- `url`: Type of URL to search for (e.g. *.gov for all .gov domains).
- `keyword`: Keyword that must be matched in the full URL
- `--pages num_pages`: Number of pages to search
- `--record-type record_type` (optional): Assumed record type for pre-annotation.

e.g. `python annotation_pipeline/populate_labelstudio.py CC-MAIN-2024-10 '*.gov' arrest --pages 2 --record-type 'Arrest Records'`
