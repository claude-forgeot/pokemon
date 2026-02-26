"""File handler module -- generic JSON file reader/writer."""

import json
import os


class FileHandler:
    """Generic JSON file reader/writer with error handling."""

    def load_json(self, path):
        """Load and return data from a JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            dict or list: Parsed JSON data.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_json(self, path, data):
        """Save data to a JSON file, creating directories if needed.

        Args:
            path: Path where the JSON file will be saved.
            data: Data to serialize (dict or list).
        """
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def file_exists(self, path):
        """Check if a file exists at the given path.

        Args:
            path: Path to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return os.path.isfile(path)
