from huggingface_hub import hf_hub_download
import pandas as pd
import subprocess
import sys
import os
import configparser

# The below code sets the working directory to be the root of the entire repository for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from label_studio_interface.LabelStudioConfig import LabelStudioConfig
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager

def run_subprocess(terminal_command: str):
    """
    Runs subprocesses (e.g. common crawl and html tag collector) and handles their outputs + errors
    """

    process = subprocess.Popen(terminal_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    with process.stdout, process.stderr:
        for line in process.stdout:
            print(line, end='')
        for line in process.stderr:
            print(line, end='')

    return_code = process.wait()

    stdout, stderr = process.communicate()

    return return_code, stdout, stderr

def run_common_crawl(common_crawl_id: str, url: str, search_term: str, num_pages: str):
    """
    Prompts terminal to run common crawl script provided the following:
    Args: SEE def process_crawl()

    See Common Crawl Documentation @ https://github.com/Police-Data-Accessibility-Project/data-source-identification/blob/main/common_crawler/README.md

    CSV of crawled URL's uploaded to HuggingFace
    """

    common_crawl = f"python ../common_crawler/main.py {common_crawl_id} '{url}' {search_term} --config ../common_crawler/config.ini --pages {num_pages}"

    return_code, stdout, stderr = run_subprocess(common_crawl)

    return return_code, stdout, stderr

def run_tag_collector(filename: str):
    """
    Prompts terminal to run tag collector on crawled URL's
    filename: name of csv containing crawled URL's

    CSV of URL's + collected tags saved in ./labeled-source-text.csv
    """
    tag_collector = f"python3 ../html_tag_collector/collector.py common_crawler/{filename} --render-javascript"

    return_code, stdout, stderr = run_subprocess(tag_collector)

    return return_code, stdout, stderr

def csv_to_label_studio_tasks(csv_file_path: str, batch_id: str, output_name: str) -> list[dict]:
    """
    Formats CSV into list[dict] with "data" key as labelstudio expects
    csv_file_path: path to csv with labeled source text
    batch_id: timestamp to append to all URL's in batch
    output_name: saves tag_collected CSV + batch_info in tag_collector/{output_name}
    """
    df = pd.read_csv(csv_file_path)
    df['batch_id'] = [batch_id] * len(df)
    df = df.fillna('')
    df.to_csv("tag_collector/" + output_name.replace("urls/", "", 1), index=False)
    tasks = [{"data": row.to_dict()} for _, row in df.iterrows()]
    return tasks

def get_huggingface_repo_id(config_file: str) -> str:
    """ Returns HuggingFace REPO_ID (where unlabeled URLs are stashed) from config.ini file"""

    config = configparser.ConfigParser()
    config.read(config_file)

    # Retrieve the huggingface_repo_id from the DEFAULT section
    huggingface_repo_id = config['DEFAULT'].get('huggingface_repo_id')
    
    if huggingface_repo_id is None:
        raise ValueError("huggingface_repo_id not found in the config file.")

    return huggingface_repo_id

def process_crawl(common_crawl_id: str, url: str, search_term: str, num_pages: str) -> pd.Series:
    """Initiated common crawl script and handles output for further processing
    
    Args:
        common_crawl_id: string to specify which common crawl corpus to search
        url: specify type of url to search for (e.g. *.gov for all .gov domains)
        search_term: further refine search with keyword that must be matched in full URL
        num_pages: number of pages to search (15,000 records per page)

    Returns: 
        batch_info (pd.Series): summary info of crawl, including filename of csv containing relevant URLs
    """
    #run common crawl
    crawl_return_code, crawl_stdout, crawl_stderr = run_common_crawl(common_crawl_id, url, search_term, num_pages)

    #check success
    if crawl_return_code != 0:
        print(f"Common crawl script failed:\n{crawl_stderr}")
        return

    #print batch info to verify before continuing
    batch_info = pd.read_csv("common_crawler/data/batch_info.csv").iloc[-1]
    print("Batch Info:\n" + f"{batch_info}")

    if(batch_info["Count"] != 0):
        input("Confirm batch info and csv on HuggingFace, press any key to proceed. Ctrl-c to quit")
    else:
        return

    #get urls from hugging face
    REPO_ID = get_huggingface_repo_id("../common_crawler/config.ini")
    FILENAME = "urls/" + batch_info["Filename"] + ".csv"
    df = pd.read_csv(hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset", local_dir="common_crawler/"), index_col=False)

    return batch_info

def process_tag_collector(batch_info: pd.Series, FILENAME: str) -> str:
    """
    Initiates tag collector script and creates a batch id for all samples

    Args:
        batch_info (pd.Series): summary info for crawl
        FILENAME (str): filename of csv to collect tags on

    Returns:
        batch_id (str): a datetime stamp to track batches
    """
    
    #run tag collector
    tag_collector_return_code, tag_collector_stdout, tag_collector_stderr = run_tag_collector(FILENAME)

    #check success
    if tag_collector_return_code != 0:
        print(f"Tag collector script failed:\n{tag_collector_stderr}")
        return

    #create batch_id from datetime (removes milliseconds)
    datetime = batch_info["Datetime"]
    batch_id = datetime[:datetime.find('.')]

    return batch_id

def label_studio_upload(batch_id: str, FILENAME: str):
    """
    Handles label studio task formatting and upload
    """
    
    #convert to label studio task format
    data = csv_to_label_studio_tasks("labeled-source-text.csv", batch_id, FILENAME)

    # Load the configuration for the Label Studio API
    config = LabelStudioConfig("dev.env")
    if "REPLACE_WITH_YOUR_TOKEN" in config.authorization_token:
        raise ValueError("Please replace the access token in dev.env with your own access token")

    # Create an API manager
    api_manager = LabelStudioAPIManager(config)

    #import tasks
    label_studio_response = api_manager.import_tasks_into_project(data)

    #check import success
    if label_studio_response.status_code == 201:
        labelstudio_url = api_manager.api_url_constructor.get_import_url().rstrip('/import')
        print(f"Tasks successfully imported. Please access the project at {labelstudio_url} to perform review and annotation tasks")
    else:
        print(f"Failed to import tasks. Response code: {label_studio_response.status_code}\n{label_studio_response.text}")

def main():
    """
    This script automates the process of crawling for relevant URL's,
    scraping HTML content from those pages, formatting the data as label studio tasks,
    and uploading to label studio
    """

    # COMMON CRAWL
    batch_info = process_crawl('CC-MAIN-2024-10', '*.gov', 'police', '2')
    FILENAME = "urls/" + batch_info["Filename"] + ".csv"

    # TAG COLLECTOR
    batch_id = process_tag_collector(batch_info, FILENAME)

    # LABEL STUDIO UPLOAD
    label_studio_upload(batch_id, FILENAME)

if __name__ == "__main__":
    print("Running Annotation Pipeline...")
    main()

