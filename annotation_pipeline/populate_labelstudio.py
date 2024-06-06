from huggingface_hub import hf_hub_download
import pandas as pd
import subprocess
import sys
import os

# Add the directory containing label studio interface tools to sys.path
script_dir = os.path.abspath('../label_studio_interface/')
sys.path.append(script_dir)

from LabelStudioConfig import LabelStudioConfig
from LabelStudioAPIManager import LabelStudioAPIManager

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
	common_crawl_id: (str)
	url: (str)
	search_term: (str)
	num_pages: (str)

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

def main():
	"""
	This script automates the process of crawling for relevant URL's,
	scraping HTML content from those pages, formatting the data as label studio tasks,
	and uploading to label studio
	"""

	# ----------------- COMMON CRAWL -----------------------------------

    #common crawl parameters
	common_crawl_id = 'CC-MAIN-2024-10'
	url = '*.gov'
	search_term = 'police'
	num_pages = '2'

    #run common crawl
	crawl_return_code, crawl_stdout, crawl_stderr = run_common_crawl(common_crawl_id, url, search_term, num_pages)

    #check success
	if crawl_return_code != 0:
		print(f"Common crawl script failed with error:\n{crawl_stderr}")
		sys.exit(1)

    #print batch info to verify before continuing
	batch_info = pd.read_csv("common_crawler/data/batch_info.csv").iloc[-1]
	print("Batch Info:\n" + f"{batch_info}")

	input("Confirm batch info and csv on HuggingFace, press any key to proceed. Ctrl-c to quit")

	#get urls from hugging face
	REPO_ID = "PDAP/unlabeled-urls"
	FILENAME = "urls/" + batch_info["Filename"] + ".csv"
	df = pd.read_csv(hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset", local_dir="common_crawler/"), index_col=False)

	# ----------------- TAG COLLECTOR ----------------------------------

    #run tag collector
	tag_collector_return_code, tag_collector_stdout, tag_collector_stderr = run_tag_collector(FILENAME)

    #check success
	if tag_collector_return_code != 0:
		print(f"Tag collector script failed with error:\n{tag_collector_stderr}")
		sys.exit(1)

	#create batch_id from datetime (removes milliseconds)
	datetime = batch_info["Datetime"]
	batch_id = datetime[:datetime.find('.')]

	# ----------------- LABEL STUDIO UPLOAD ----------------------------

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
        sys.exit(1)

if __name__ == "__main__":
    print("Running Annotation Pipeline...")
    main()



