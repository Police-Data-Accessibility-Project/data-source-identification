import csv
import os

from util.miscellaneous_functions import get_file_path


class CSVManager:
    """
    Manages a CSV file for storing URLs.
    Creates the file if it doesn't exist, and provides a method for adding new rows.
    """

    def __init__(
            self,
            file_name: str,
            headers: list[str],
            directory=None
    ):
        self.file_path = get_file_path(f"{file_name}.csv", directory)
        self.headers = headers
        if not os.path.exists(self.file_path):
            self.initialize_file()

    def add_row(self, row_values: list[str] | tuple[str]):
        """
        Appends a new row of data to the CSV.
        Args:
            row_values: list of values to add to the csv, in order of their inclusion in the list
        """
        if isinstance(row_values, str):
            # Single values must be converted to a list format
             row_values = [row_values]
        try:
            with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(row_values)
        except Exception as e:
            print(f"An error occurred while trying to write to {self.file_path}: {e}")

    def add_rows(self, results: list[list[str]]) -> None:
        """
        Appends multiple rows of data to the CSV as a list of lists of strings.
        Args:
            results: list[list[str] - a list of lists of strings, each inner list representing a row
        Returns: None
        """
        for result in results:
            self.add_row(
                result
            )
        print(f"{len(results)} URLs written to {self.file_path}")

    def initialize_file(self):
        """
        Initializes the CSV file.
        If the file doesn't exist, it creates it with the header row.
        """
        # check if file exists
        file_exists = os.path.isfile(self.file_path)

        if not file_exists:
            with open(self.file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)
        else:
            # Open and check that headers match
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                header_row = next(csv.reader(file))
                if header_row != self.headers:
                    raise ValueError(f"Header row in {self.file_path} does not match expected headers")
        print(f"CSV file initialized at {self.file_path}")

    def delete_file(self):
        """
        Deletes the CSV file.
        """
        os.remove(self.file_path)
        print(f"CSV file deleted at {self.file_path}")
