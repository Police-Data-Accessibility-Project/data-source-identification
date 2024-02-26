"""
Preprocess urls from relevant dataset by adding associated html content
Then loads the urls to the target database

Contains abstract classes for both DataSource and DataTarget, to be implemented by the actual source and target classes
"""

from abc import ABC, abstractmethod
import csv
import logging

from AnnotationHelper.harvest_html import harvest_html


class DataSource(ABC):
    """
    Abstract class for loading data from a source
    """

    @abstractmethod
    def load_urls(self) -> list[str]:
        pass


class DataTarget(ABC):
    """
    Abstract class for loading data to a target destination
    """

    @abstractmethod
    def upload_data(self, data: dict[str, str]) -> None:
        """
        Uploads the data to the target destination
        Args:
            data: dictionary of urls and their associated html content

        Returns: None

        """
        pass


"""
Below are example concrete classes for the abstract classes above
"""


class CsvDataSource(DataSource):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_urls(self) -> list[str]:
        urls = []
        with open(self.file_path, mode='r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                urls.append(row[0])  # Assuming the URL is in the first column
        return urls


class PrintDataTarget(DataTarget):
    def upload_data(self, data: dict[str, str]) -> None:
        for url, html in data.items():
            print(f"URL: {url}, HTML Content: {len(html)} characters")


def preprocess_and_load_urls(source: DataSource, target: DataTarget) -> None:
    """
    Preprocess urls from relevant dataset by adding associated html content
    Then loads the urls to the target database
    Args:
        source: DataSource object
        target: DataTarget object

    Returns: None

    """

    try:
        urls = source.load_urls()
        logging.info(f"Loaded {len(urls)} URLs from the data source.")
    except Exception as e:
        logging.error(f"Failed to load URLs from data source: {e}")
        return  # Optionally, return or raise based on your error handling policy

    try:
        html_content = harvest_html(urls)
        logging.info("Successfully harvested HTML content for all URLs.")
    except Exception as e:
        logging.error(f"Failed to harvest HTML content: {e}")
        return  # Adjust based on your policy

    try:
        target.upload_data(html_content)
        logging.info("Data successfully uploaded to target.")
    except Exception as e:
        logging.error(f"Failed to upload data to target: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    data_source = CsvDataSource(file_path='urls.csv')  # Replace with actual source
    data_target = PrintDataTarget()  # Replace with actual target
    preprocess_and_load_urls(data_source, data_target)
