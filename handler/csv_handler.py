#######################################################
# @Project: Telemetry
# @Module: csv_handler.py
# @Description: This module provides a handler for exporting telemetry data to CSV files.
# @Author: AbigailWilliams1692
# @CreationDate: 2025-07-23
#######################################################

#######################################################
# Import Libraries
#######################################################
# Standard Libraries
import csv
import os

# Third-Party Libraries

# Local Libraries
from handler.handler import Handler


#######################################################
# Class: CSVHandler
#######################################################
class CSVHandler(Handler):
    """
    Handler for exporting telemetry data to CSV files.
    """

    ######################################################
    # Default Methods
    ######################################################
    def __init__(self, output_file_path: str) -> None:
        """
        Constructor for the CSVHandler class.

        :param output_file_path: Path to the CSV file where records will be exported.
        """
        super().__init__()
        if self.validate_folder_path_of_the_file(file_path=output_file_path):
            self.output_file_path = output_file_path
        else:
            raise FileNotFoundError(f"The folder path for the output file does not exist or is invalid: {output_file_path}")

    def __str__(self) -> str:
        """
        Returns a string representation of the CSVHandler instance.
        """
        return f"CSVHandler<{id(self)}>"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the CSVHandler instance.
        """
        return self.__str__()

    ######################################################
    # Core Methods
    ######################################################
    def export(self, records: list[dict]) -> None:
        """
        Exports telemetry records to a CSV file.

        :param records: List of telemetry records to export.
        """
        # Get whether the csv file already exists
        if_already_exists = os.path.exists(self.output_file_path)

        # Write the records to the CSV file
        if not records:
            return
        else:
            with open(self.output_file_path, mode="a", newline="", encoding="utf-8") as csvfile:
                # Write the column headers only if the file does not already exist
                column_headers = records[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=column_headers)

                # Check if the file already exists to determine whether to write headers
                if not if_already_exists:
                    writer.writeheader()

                # Write the records to the CSV file
                writer.writerows(records)

    ######################################################
    # Utility Methods
    ######################################################
    @staticmethod
    def validate_folder_path_of_the_file(file_path: str) -> bool:
        """
        Validates the folder path of the given file.

        :param file_path: Path to the file to validate.
        :return : True if the folder path exists, False otherwise.
        """
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(folder_path):
            return False
        return True
