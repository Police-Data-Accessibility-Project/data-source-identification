import csv
import os

from util.miscellaneous_functions import get_file_path


class CSVManager:
    """
    Manages a CSV file for storing URLs.
    Creates the file if it doesn't exist, and provides a method for adding new rows.
    """

    def __init__(self, file_name: str = 'urls', directory=None):
        self.file_path = get_file_path(f"{file_name}.csv", directory)
        if not os.path.exists(self.file_path):
            self.initialize_file()

    def add_row(self, url: str):
        """
        Appends a new row of data to the CSV.
        Data should be a list or tuple in the format:
        (index, search_term, keyword, page, url)
        """
        try:
            with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([url])
        except Exception as e:
            print(f"An error occurred while trying to write to {self.file_path}: {e}")

    def add_rows(self, results: list) -> None:
        """
        Appends multiple rows of data to the CSV.
        Args:
            results: list[UrlResults] - a list of UrlResults named tuples
        Returns:
        """
        for result in results:
            self.add_row(
                url=result
            )
        print(f"{len(results)} URLs written to {self.file_path}")

    def initialize_file(self):
        """
        Initializes the CSV file.
        If the file doesn't exist, it creates it with the header row.
        If the file does exist, it empties it, leaving only the header row.
        """
        with open(self.file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['url'])
        print(f"CSV file initialized at {self.file_path}")

    def delete_file(self):
        """
        Deletes the CSV file.
        """
        os.remove(self.file_path)
        print(f"CSV file deleted at {self.file_path}")
